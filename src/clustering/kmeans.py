# This script is built on the code presented in: https://towardsdatascience.com/how-to-cluster-images-based-on-visual-similarity-cd6e7209fe34
# Last accessed: June 28, 2021

import logging
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import src.database.db_connector as db
from dotenv import load_dotenv
from numpy.typing import ArrayLike
# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import load_img

from ..util.plotting import plot_distribution, plots_from_list

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))

# initalize logging
log = logging.getLogger("training")

# global variables to create clustering run name, will be overwritten
clustering_run_name = None
dataset_name = None
model_annotation = None

# global variable for cluster amount, will be overwritten
k = None
k_low = None  # lower bound to start iteration
k_high = None  # upper bound to end iteration

# directory for dataset
datadir = None

# database name for results
db_name = "clustering_db"
cnx = None
cursor = None

# within cluster sum of squared errors for different k's
sse = []

# silhouette score for different k's
sil = []


def load_dataset(name: str) -> Tuple[List[str], Model]:
    """Loads a local dataset with name `dataset_name` and the pretrained VGG16 model.

    Args:
        dataset_name (str): the name of the dataset to be loaded

    Returns:
        Tuple[List[str], Model]: (file list of dataset, pretrained model)
    """
    global datadir
    datadir = (
        DATA_PATH / "datasets" / ("dataset_" + name + "_root") / ("dataset_" + name)
    )

    images = []

    with os.scandir(datadir) as files:
        for file in files:
            images.append(file.name)

    # load pretrained VGG16 model
    model = VGG16()
    # remove output layer
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    return (images, model)


def extract_features(file_name: str, model: Model) -> ArrayLike:
    """Extracts the features for an image file using the specified (pre-trained) model.

    Args:
        file_name (str): the name of image file
        model (Model): pretrained model for feature prediction

    Returns:
        ArrayLike: predictions for the image
    """
    # load the image as a 224x224 array
    img = load_img(datadir / file_name, target_size=(224, 224))

    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img)

    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1, 224, 224, 3)

    # prepare image for model
    imgx = preprocess_input(reshaped_img)

    # get the feature vector using pre-trained model
    features = model.predict(imgx, use_multiprocessing=True)
    return features


def run_pca(features: ArrayLike, n_components: int) -> ArrayLike:
    """Reduce the amount of dimensions in the feature vector to `n_components`.

    Args:
        features (ArrayLike): array-like of shape (n_samples, n_features)
        n_components (int): [description]

    Returns:
        ArrayLike: X_reduced features
    """
    pca = PCA(n_components=n_components, random_state=22)
    pca.fit(features)
    features_reduced = pca.transform(features)
    return features_reduced, pca


def preview_cluster(
    cluster_files: List[str], cluster_idx: int = 0, cluster_name: str = None
) -> None:
    """Preview images of the specified cluster in a subplot.

    Args:
        cluster_files (List[str]): all files belonging to cluster
        cluster_idx (int, optional): index of the cluster
    """
    cluster_len = len(cluster_files)

    # only allow up to 10 images to be shown at a time
    if len(cluster_files) > 10:
        cluster_files = cluster_files[:10]

    # show cluster name
    ax = plt.subplot(k, 10 + 1, 1 + max(cluster_idx, 0) * 11)
    ax.axis("off")
    ax.text(0.3, 0.4, f"{cluster_name}\nlen: {cluster_len}")

    # plot each image in the cluster
    for index, file in enumerate(cluster_files):
        # calculate img index in plot
        idx = index + 1 + 1 + (max(cluster_idx, 0) * 11)
        img = load_img(datadir / file)

        plt.subplot(k, 10 + 1, idx)
        plt.imshow(img)
        plt.axis("off")


def preview_all_clusters(
    clusters: Dict[Any, List[str]],
    title: str,
    save: bool = False,
) -> None:
    """Plot previews for all clusters.

    Args:
        clusters (Dict[Any, List[str]]): dict of all clusters with file names
        title (str): title of the plot and filename if save is `True`.
        save (bool, optional): `True` to save file. Defaults to False.

    """
    if save:
        # get or create target directoy
        model_dir = Path(DATA_PATH) / "plots" / "clustering" / clustering_run_name
        if not model_dir.is_dir():
            model_dir.mkdir(parents=True, exist_ok=True)

        # specify target file
        target_file = model_dir / (title + ".jpg")
        if target_file.is_file():
            log.warning(f"File with name {title} already exists, not overwriting.")

    plt.clf()
    # Different backend that does not show plots to user
    matplotlib.use("Agg")
    plt.figure(figsize=(20 + 2, 2 * k))
    plt.suptitle(title, fontsize=15)

    # line number for plot
    i = 0

    for key in clusters:
        preview_cluster(clusters[key], i, key)
        i += 1
    plt.ylabel(clusters.keys)

    if save:
        plt.savefig(target_file)
    else:
        plt.show()


def store_clusters(
    run_name: str,
    k_value: int,
    n_screenshots: int,
    n_components: int,
    clusters: Dict[str, List[str]],
) -> None:
    """Store clusters in database.

    Args:
        run_name (str): name of the clustering run
        k_value (int): k-value of clustering run
        n_screenshots (int): total number of screenshots
        n_components (int): number of pca components
        clusters (Dict[str, List[str]]): dict of clusters
    """
    path_prefix = "screenshots\\raw\\"

    try:
        db.insert_clustering_run(
            db_name, run_name, k_value, n_screenshots, n_components, cursor
        )
        cnx.commit()
        log.info(f"Finished inserting clustering run")
    except Exception:
        cnx.rollback()
        # return to avoid duplicates
        return

    for cluster_id in clusters:
        # store cluster properties
        try:
            db.insert_cluster(
                db_name,
                str(cluster_id),
                run_name,
                k_value,
                len(clusters[cluster_id]),
                cursor,
            )
            cnx.commit()
        except Exception:
            cnx.rollback()
            # do not continue, so more screenshots can be added to cluster

        # store file-to-cluster mappings
        for filename in clusters[cluster_id]:
            scr_id = db.get_screenshot_by_path(db_name, path_prefix + filename, cursor)

            if scr_id is None:
                continue

            try:
                db.insert_cluster_assignment(
                    db_name, str(cluster_id), run_name, k_value, scr_id[0], cursor
                )
                cnx.commit()
            except Exception:
                cnx.rollback()
                continue
        log.info(f"Finished inserting cluster {cluster_id}")


def run_kmeans(
    X: ArrayLike, k: int, n_components: Union[float, int]
) -> Tuple[KMeans, ArrayLike]:
    """Perform K-Means clustering with `k` clusters on `X`.

    Args:
        X (ArrayLike): array-like of shape (n_samples, n_features)
        k (int): value for k
        n_components (Union[float, int]): pca components value

    Returns:
        Tuple[KMeans, ArrayLike]: (kmeans instance, cluster assignments)
    """

    model_dir = DATA_PATH / "models" / "clustering"
    model_name = (
        f"{dataset_name}_k_{str(k)}_pca_{str(n_components).replace('.','_')}.mdl"
    )

    # check if k-means model exists
    model_file = search_dir(model_dir, model_name)
    if model_file:
        log.info(f"Loading K-Means model {model_file}")
        # load kmeans model and predict labels
        with open(model_file, "rb") as pickle_file:
            kmeans = pickle.load(pickle_file)
            kmeans_labels = kmeans.predict(X)
    else:
        # create new k-means model
        log.info(f"Creating new K-Means model with k={str(k)}")
        kmeans = KMeans(n_clusters=k, random_state=22, max_iter=300)
        kmeans_labels = kmeans.fit_predict(X)

    global sse, sil
    # within cluster sum of squared errors
    sse.append(kmeans.inertia_)

    # silhouette_score
    sil.append(silhouette_score(X, kmeans.labels_, metric="euclidean"))

    return (kmeans, kmeans_labels)


def init_training() -> Dict[str, ArrayLike]:
    """Prepare environment and data for training.

    Returns:
        Dict[str, ArrayLike]: prepared training data
    """
    # load dataset and model
    dataset, model = load_dataset(dataset_name)

    # check if extracted features already exist
    extract_features_dir = DATA_PATH / "extracted_features"
    src_file = "features_" + dataset_name + ".pickle"
    extracted_features_file = search_dir(extract_features_dir, src_file)

    if extracted_features_file:
        # if features have already been extracted, return them
        with open(extracted_features_file, "rb") as pickle_file:
            data = pickle.load(pickle_file, encoding="utf-8")

            log.info(f"Using extracted features from file {src_file}")
            return data

    # extract features if not found
    data = {}
    log.info("Running feature extraction..")
    for image in dataset:
        # try to extract the features and update the dictionary
        try:
            feat = extract_features(image, model)
            data[image] = feat
        # if something fails, save the extracted features as a pickle file (optional)
        except Exception as err:
            log.error(err)

    # store extracted features
    with open(extract_features_dir / src_file, "wb") as target_file:
        pickle.dump(data, target_file)

    # return extracted features
    return data


def run_training(args: List[any]):
    """Run the clustering training."""

    global dataset_name, model_annotation, k_low, k_high
    # get cli parameters
    dataset_name = args[0]
    model_annotation = args[1]
    k_low = int(args[2])
    k_high = int(args[3]) + 1

    # set step size for different k values
    if len(args) >= 5:
        k_steps = int(args[4])
    else:
        k_steps = 1

    # set n_component value
    if len(args) >= 6:
        n_components = float(args[5])
    else:
        n_components = 0.8

    global clustering_run_name
    clustering_run_name = dataset_name + "_" + model_annotation
    log.info(
        f"Starting clustering run {clustering_run_name} with {n_components} pca components"
    )

    # Connecting to database, exceptions intentionally crash
    global cnx, cursor
    cnx = db.connect_to_database(db_name)
    cursor = db.get_connection_cursor(cnx)

    data = init_training()

    # get a list of the filenames
    filenames = np.array(list(data.keys()))

    # get a list of just the features
    feat = np.array(list(data.values()))

    # reshape so that there are 210 samples of 4096 vectors
    feat = feat.reshape(-1, 4096)

    log.info("Running PCA..")

    # cast to int if n_components is not a percentage
    n_components = int(n_components) if n_components > 1 else n_components
    X_reduced = run_pca(feat, n_components)[0]

    # list to store plots
    plots_list = []

    global k

    # cluster feature vectors for different k's
    list_k = [x for x in range(k_low, k_high, k_steps)]
    for k_value in list_k:
        # --- CLUSTERING START ---
        k = k_value
        log.info(f"Running k-means for {str(k)} clusters")
        kmeans, kmeans_labels = run_kmeans(X_reduced, k, n_components)
        log.info(f"K-Means for k={str(k)} completed")

        # sort clusters ascendingly
        kmeans_cluster_assignments = list(zip(filenames, kmeans_labels))
        kmeans_cluster_assignments.sort(key=lambda x: x[1])

        # store filenames for each cluster
        kmeans_clusters = {}  # Dict[Any, List[str]]

        for file, cluster in kmeans_cluster_assignments:
            if cluster not in kmeans_clusters.keys():
                kmeans_clusters[cluster] = []
                kmeans_clusters[cluster].append(file)
            else:
                kmeans_clusters[cluster].append(file)

        # get cluster centroids
        centroids = kmeans.cluster_centers_
        if centroids is None:
            log.warning("Centroids are empty")

        # calculate cluster sizes
        kmeans_cluster_sizes = np.bincount(
            list(map(lambda tpl: tpl[1], kmeans_cluster_assignments))
        )

        # --- PLOTTING ---
        log.info(f"Plotting for k={str(k)}")
        # plot_distribution(
        #     kmeans_labels,
        #     X_reduced,
        #     centroids,
        #     save=True,
        #     title=(clustering_run_name + "_distribution_k" + str(k)),
        #     parent_folder=(clustering_run_name),
        # )

        # create bar plot for cluster sizes
        plt.clf()
        bar_plot = (
            plt.bar,
            {
                "x": list(range(0, len(kmeans_cluster_sizes))),
                "height": kmeans_cluster_sizes,
            },
            f"Cluster Sizes for k={k}",
            "clusters",
            "size",
        )
        plots_list.append(bar_plot)

        # plot preview for all
        preview_all_clusters(
            kmeans_clusters, f"Cluster Preview for k={str(k)}", save=True
        )

        # --- STORE RESULTS ---
        log.info(f"Storing clusters for k={str(k)} in db")
        store_clusters(
            clustering_run_name,
            k,
            len(filenames),
            n_components,
            kmeans_clusters,
        )

        model_name = (
            f"{dataset_name}_k_{str(k)}_pca_{str(n_components).replace('.','_')}"
        )
        store_model_to_file(kmeans, model_name, "clustering")

        log.info(f"Finished clustering for k={str(k)}")
        # --- CLUSTERING END ---

    # plot WSS
    # wss_title = clustering_run_name + "_wss"
    wss_title = "Weighted Sum of Within-Cluster Squared Distance"
    wss_plot = (
        plt.plot,
        [list_k, sse],
        wss_title,
        f"Number of clusters k",
        "Sum of squared distance",
    )
    plots_list.append(wss_plot)

    # silhouette score
    # sil_title = clustering_run_name + "_silhouette_score"
    sil_title = "Silhouette Score"
    sil_plot = (
        plt.plot,
        [list_k, sil],
        sil_title,
        f"Number of clusters k",
        "Silhouette score",
    )
    plots_list.append(sil_plot)

    # save plots as document
    plots_from_list(
        clustering_run_name + "_wss_sil",
        plots_list,
        parent_folder=clustering_run_name,
        save=True,
    )
    log.info(f"Completed clustering run {clustering_run_name}")


def test_pca_components(args: List[any]):
    """Runs PCA with a specified value for `n_components`.

    Args:
        args (List[any]): list of command line arguments
    """
    global dataset_name, model_annotation
    # get cli parameters
    dataset_name = args[0]
    n_components = float(args[1])
    log.info(f"Running pca on dataset {dataset_name} with {n_components} components")

    data = init_training()

    # get a list of just the features
    feat = np.array(list(data.values()))

    # reshape so that there are 210 samples of 4096 vectors
    feat = feat.reshape(-1, 4096)

    log.info("Running PCA..")
    pca = run_pca(feat, int(n_components) if n_components > 1 else n_components)[1]

    log.info(f"Amount explained: {str(sum(pca.explained_variance_ratio_))}")
    log.info(f"Amount explained in each PC: {str(pca.explained_variance_ratio_)}")
    log.info(f"Used components: {str(len(pca.components_))}")


def store_model_to_file(model, model_name: str, model_type: str):
    """Store the specified as a `.mdl` file.

    Args:
        model ([type]): the model to be stored
        model_name (str): name of the file
        model_type (str): parent folder name (`gan` or `clustering`)
    """
    model_dir = DATA_PATH / "models" / model_type

    if not model_dir.is_dir():
        model_dir.mkdir(parents=True, exist_ok=True)

    target_file = model_dir / (model_name + ".mdl")
    if not target_file.is_file():
        pickle.dump(model, open(model_dir / (model_name + ".mdl"), "wb"))
        log.info(f"Stored model {model_name} as in {str(model_dir)}")
    else:
        log.warning(f"Model {model_name} already exists, not overwritting")


def search_dir(dir: Union[Path, str], filename: str) -> Optional[Path]:
    """Search the specified directory for a file.

    Args:
        dir (Union[Path, str]): the directory to search within
        filename (str): target file

    Returns:
        Optional[Path]: complete path to file, or None.
    """
    log.info(f"Scanning dir {dir} for file {filename}..")
    with os.scandir(dir) as files:
        file_list = [entry.name for entry in files if entry.is_dir() or entry.is_file()]

        if filename in file_list:
            log.info(f"Found file {filename}")
            return Path(dir) / filename
        else:
            # file not found
            log.info(f"No such file {filename}")
            return None


if __name__ == "__main__":
    run_training()

import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from numpy.typing import ArrayLike

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")


def disp_scatter(
    x: any,
    y: any,
    x_label: str = None,
    y_label: str = None,
    plot_name: str = None,
):
    """Displays a scatter plot.

    Args:
        x (any): list of data for x-axis
        y (any): list of data for y-axis data
        x_label (str, optional): label for x-axis. Defaults to None.
        y_label (str, optional): label for y-axis. Defaults to None.
        plot_name (str, optional): title of plot. Defaults to None.
    """
    plt.title(plot_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.scatter(x, y, s=5, alpha=0.5)
    plt.show()


def plot_distribution(
    labels: ArrayLike,
    X: ArrayLike,
    centroids=None,
    save: bool = False,
    title: str = None,
    parent_folder: str = None,
) -> None:
    """Plot the distribution of images as individuals as a scatter plot.

    Args:
        labels (ArrayLike): predicted cluster for each image

        X (ArrayLike): ndarray of shape (n_clusters, n_features)

        centroids (NDArray, optional): ndarray of shape (n_clusters, n_features)

        save (bool, optional): `True` to save file. Defaults to `False`.

        title (str, optional): title on the document + file name. Defaults to `None`.

        parent_folder (str, optional): name of parent folder for file. Defaults to `None`.

    """
    if save:
        # get or create target directoy
        model_dir = Path(DATA_PATH) / "plots" / "clustering" / parent_folder
        if not model_dir.is_dir():
            model_dir.mkdir(parents=True, exist_ok=True)

        # specify target file
        target_file = model_dir / (title + ".jpg")
        if target_file.is_file():
            raise ValueError(f"File with name {title} already exists.")

    # Get unique labels
    unique_labels = np.unique(labels)

    # plot the results
    plt.clf()

    # heatmap, xedges, yedges = np.histogram2d([x[0] for x in X], labels, bins=50)
    # extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    # plt.imshow(heatmap.T, extent=extent, origin="lower")

    # for i in unique_labels:
    #     plt.scatter(X[labels == i, 0], X[labels == i, 1], label=i)
    # plt.legend()

    # # plot cluster centroids
    # if centroids is not None:
    #     plt.scatter(centroids[:, 0], centroids[:, 1], s=80, color="k")

    if save:
        # Different backend that does not show plots to user
        matplotlib.use("Agg")
        plt.savefig(target_file)
    else:
        plt.show()


def plots_from_list(
    title: str,
    plots: List[Tuple[Callable, Union[Dict[str, Any], List[Any]], str, str, str]],
    parent_folder: str = None,
    text: str = None,
    save: bool = False,
    cols: int = 2,
):
    """Create a figure from a list of plots. Stored as pdf if save is True.

    Args:
        title (str): title on the document + file name

        plots (ist[Tuple[Callable, Union[Dict[str, Any], List[Any]], str, str, str]]): list of tuples:
            (plot function, plot function arguments, title, xlabel, ylabel)

        text (str): information to be printed on top of the document. Defaults to None.

        parent_folder (str, optional): name of parent folder for pdf. Defaults to `None`.

        save (bool, optional): true to save file. Defaults to False.

        cols (int, optional): number of columns of generated figure. Defaults to 2.

    Raises:
        ValueError: File with `file_name` already exists
    """

    if save:
        # get or create target directoy
        model_dir = Path(DATA_PATH) / "plots" / "clustering" / parent_folder
        if not model_dir.is_dir():
            model_dir.mkdir(parents=True, exist_ok=True)

        # specify target file
        target_file = model_dir / (title + ".jpg")
        if target_file.is_file():
            # raise ValueError(f"File with name {title} already exists.")
            print(f"File with name {title} already exists.")
            return 

    # create plot
    fig = plt.figure(figsize=(cols * 6, (len(plots) * 3)))
    fig.suptitle(title, fontsize=15)

    # add text
    if text:
        ax = fig.add_subplot(cols, 1, 1)
        ax.text(x=0.05, y=0.9, s=(text), wrap=True)
        plt.axis("off")

    # map list on subplots
    for idx, plot_data in enumerate(plots, start=(cols + 1)):
        ax = fig.add_subplot(cols + int(math.ceil((len(plots) / cols))), cols, idx)
        ax.set_title(plot_data[2])
        ax.set_xlabel(plot_data[3])
        ax.set_ylabel(plot_data[4])

        # for confusion matrix, add axis to arguments
        fun = plot_data[0]

        if fun != "text" and fun.__name__ == "plot_confusion_matrix":
            plot_data[1]["ax"] = ax

        if fun == "text":
            # call text function of axis with arguments in dict at [1]
            ax.text(**plot_data[1])
            plt.axis("off")
        else:
            if isinstance(plot_data[1], dict):
                # call plot function at [0] with arguments in dict at [1]
                plot_data[0](**plot_data[1])
                ax.set_xticks(plot_data[1]["x"])
            elif isinstance(plot_data[1], list):
                # call plot function at [0] with arguments in list at [1]
                plot_data[0](*plot_data[1])
                ax.set_xticks(plot_data[1][0])

    # spacing between plots
    fig.tight_layout()

    if save:
        # Different backend that does not show plots to user
        matplotlib.use("Agg")
        fig.savefig(target_file)
    else:
        plt.show()

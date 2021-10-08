import logging
import os
from pathlib import Path
from shutil import copy2
from typing import Any, List

import pandas as pd
from dotenv import load_dotenv

from ..database import db_connector as db
from .datasets_config import datasets_config

log = logging.getLogger("dataset")

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")
db_name = "clustering_db"
cnx = None
cursor = None

dataset_screenshot_paths = []
dataset_path = None
dataset = None


def init_creator(
    use_config: bool = False,
    dataset_name: str = None,
    run_name: str = None,
    k_value: int = None,
    cluster_id: int = None,
):
    """Initializes the location for the dataset and gets the paths of the source files from the database.

    Args:
        use_config (bool): use datasets_config.py as source. Defaults to False.
        dataset_name (str): the name of the dataset config. Defaults to None.
        run_name (str): name of clustering run. Defaults to None.
        k_value (int): k value of run. Defaults to None.
        cluster_id (int): id of cluster to use as dataset source. Defaults to None.
    """
    global dataset_screenshot_paths, dataset_path, dataset, cursor

    log.info("Connecting to database")
    try:
        cnx = db.connect_to_database(db_name)
        cursor = db.get_connection_cursor(cnx)
        log.info("Connected to database")
    except Exception as err:
        log.critical(f"Connecting to database failed: {err}")
        log.info("Exiting program")
        exit(1)

    if use_config:
        # load dataset from config file
        try:
            dataset = datasets_config[dataset_name]
        except KeyError as err:
            log.critical(
                f"Dataset config for dataset {dataset_name} does not exist: {err}"
            )
            log.info("Exiting program")
            exit(1)
        except Exception as err:
            log.critical(f"Error while reading dataset config: {err}")
            log.info("Exiting program")
            exit(1)

        # get paths from query
        # query = create_screenshot_paths_query()
        query = create_screenshot_paths_2_labels()
        dataset_screenshot_paths = get_screenshot_paths(query)
    else:
        log.info(
            f"Creating dataset from SQL query: {run_name}, k={k_value}, cluster {cluster_id}"
        )

        # load dataset from sql query
        dataset_screenshot_paths = pd.read_sql(
            screenshot_paths_from_cluster(run_name, k_value, cluster_id), cnx
        ).values

    # create destination path
    dataset_path = (
        Path(DATA_PATH) / "datasets" / (dataset_name + "_root") / (dataset_name)
    )

    # check target directory
    if not dataset_path.is_dir():
        log.info("Dataset path is not a directory or does not exist")
        log.info(f"Creating directory at {dataset_path}")

        # create directory and parent directory
        dataset_path.mkdir(parents=True, exist_ok=True)

    log.info(f"Path to dataset is {dataset_path}")
    log.info("Creator initialized")


def run_creator(args: List[Any]):
    """Run the dataset creator to create a dataset with the specified name

    Args:
        args (List[any]): command line arguments. Either

            [use_config = True, dataset name] or

            [use_config = False, dataset name, run_name, k_value, cluster_id]
    """
    log.info("Running creator")

    # get cmd line arguments
    use_config = bool(args[0])
    dataset_name = args[1]

    if use_config == "True":
        # create dataset from datasets_config.py
        init_creator(use_config=True, dataset_name=dataset_name)
    else:
        # create dataset from sql query
        run_name = args[2]
        k_value = str(args[3])
        cluster_id = str(args[4])
        init_creator(
            use_config=False,
            dataset_name=dataset_name,
            run_name=run_name,
            k_value=k_value,
            cluster_id=cluster_id,
        )

    skipped_files = []
    dataset_len = len(dataset_screenshot_paths)

    for row in dataset_screenshot_paths:
        # create target path
        file_name = row[0].split("\\")[-1]
        target_path = dataset_path / file_name

        # check if file at target path already exists
        if target_path.is_file():
            log.info(f"Already copied screenshot with filename {file_name}")
            continue

        # copy screenshot to target_path
        try:
            dest = copy2(Path(DATA_PATH) / row[0], target_path)
        except Exception as err:
            log.error(
                f"Error while copying screenshot from {Path(DATA_PATH) / row[0]} to {target_path}"
            )
            log.info(f"Skipping file {row[0]}")
            skipped_files.append(row[0])
            continue
        else:
            log.info(f"Copied screenshot to {target_path}")

    skipped_len = len(skipped_files)
    if skipped_len > 0:
        log.warning(f"Skipped {skipped_len} screenshots")

    log.info(f"Created dataset at {dataset_path} of length {dataset_len - skipped_len}")


def get_screenshot_paths(query: str) -> List[str]:
    """Returns the screenshots' paths labeled with included_labels and not excluded_labels.

    Args:
        query (str): the MYSQL query for the database

    Returns:
        List[str]: the list of source paths
    """

    # for easier logging
    excluded_labels_string = ", ".join(dataset["excluded_labels"])
    included_labels_string = (" " + dataset["include_operator"] + " ").join(
        dataset["included_labels"]
    )

    log.info(f"Including label(s) {included_labels_string}")
    log.info(f"Excluding label(s) {excluded_labels_string}")

    # execute query
    try:
        cursor.execute(query)
    except Exception as err:
        log.critical(
            f"Retrieving screenshots labeled with {included_labels_string} failed: {err}"
        )
        log.info("Exiting program")
        exit(1)

    # fetch results
    try:
        paths = cursor.fetchall()
    except Exception as err:
        log.critical(f"Error while fetching screenshot paths from cursor: {err}")
        log.info("Exiting program")
        exit(1)

    no_screenshot_paths = len(paths)
    if no_screenshot_paths <= 100:
        log.warning(
            f"Fetched {len(paths)} screenshots labeled with {included_labels_string} from database"
        )
    else:
        log.info(
            f"Fetched {len(paths)} screenshots labeled with {included_labels_string} from database"
        )
    return paths


def create_screenshot_paths_query() -> str:
    """Creates a MYSQL query for the screenshots' paths labeled with included_labels and not excluded_labels.

    Returns:
        str: the created MYSQL query
    """
    # create query to include websites with given labels
    if dataset["include_operator"] == "AND":
        included_labels_query = " AND ".join(
            list(
                map(lambda label: f"labels.name='{label}'", dataset["included_labels"])
            )
        )
    elif dataset["include_operator"] == "OR":
        included_labels_query = " OR ".join(
            list(
                map(lambda label: f"labels.name='{label}'", dataset["included_labels"])
            )
        )
    else:
        log.critical(
            f"Error while creating included_labels_query: unknown include operator {dataset['include_operator']}"
        )
        log.info("Exiting program")
        exit(1)

    # query to exclude websites with labels from excluded_labels
    excluded_labels_query = " OR ".join(
        list(map(lambda label: f"L.name='{label}'", dataset["excluded_labels"]))
    )

    # get screenshots labeled with included_labels and not with excluded_labels
    return f"""
        SELECT DISTINCT screenshots.image_path
        FROM websites 
        INNER JOIN screenshots ON websites.url=screenshots.page_url 
        INNER JOIN website_labels ON websites.id=website_labels.website_id
        INNER JOIN labels ON website_labels.label_id=labels.id 
        WHERE websites.page_type='n' 
        AND screenshots.image_path IS NOT NULL
        AND ({included_labels_query})
        AND NOT EXISTS (
            SELECT * 
            FROM website_labels as WL INNER JOIN labels as L ON WL.label_id=L.id 
            WHERE WL.website_id = websites.id AND ({excluded_labels_query})
        );
    """


def create_screenshot_paths_2_labels() -> str:
    """Creates a MYSQL query for the screenshots' paths labeled with 1 included_label and not labeled with 1 excluded_label.

    Returns:
        str: the created MYSQL query
    """
    # screenshots labeled with 1 included_label and not with 1 excluded_label
    return f"""
        SELECT DISTINCT screenshots.image_path
        FROM websites 
        INNER JOIN screenshots ON websites.url=screenshots.page_url 
        INNER JOIN website_labels ON websites.id=website_labels.website_id
        INNER JOIN labels ON website_labels.label_id=labels.id 
        WHERE websites.page_type='n' 
        AND labels.name='{dataset['included_labels'][0]}'
        AND EXISTS (
            SELECT NULL
            FROM website_labels AS WL
            JOIN labels AS L ON L.id = WL.label_id
            where websites.id = WL.website_id
            AND L.name='{dataset['included_labels'][1]}'
        );
    """


def screenshot_paths_from_cluster(run_name: str, k_value: int, cluster_id: int) -> str:
    """Return query as string for all screenshot paths for a specific cluster.

    Args:
        run_name (str): name of the clustering run
        k_value (int): k value of run
        cluster_id (int): cluster id

    Returns:
        str: query to get all screenshot paths for cluster
    """
    return f"""
        SELECT s.image_path
        FROM cluster_screenshots cs
        INNER JOIN screenshots s ON s.id = cs.screenshot_id
        WHERE cs.run_name = '{run_name}' AND cs.k_value = {str(k_value)} and cs.cluster_id = {str(cluster_id)};
    """

import json
import logging
import os
from pathlib import Path
from typing import Any, List

import pandas as pd
import src.database.db_connector as db
from dotenv import load_dotenv

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))


def create_dataset_json(args: List[Any]):
    """Creates a json file for StyleGAN2 conditional-class training from a given `run_name` and `k_value`.

    Args:
        args (List[Any]): command line arguments [run_name, k_value, Optional: filename, source_path]
    """
    # get cmd line arguments
    run_name = args[0]
    k_value = int(args[1])

    if len(args) > 2:
        filename = args[2]
    else:
        filename = "dataset.json"

    if len(args) > 3:
        source_path = args[3]
    else:
        source_path = ""

    # connect to db
    db_name = "clustering_db"
    cnx = db.connect_to_database(db_name)

    # create query
    query = """
        SELECT s.image_path, cs.cluster_id
        FROM cluster_screenshots cs
        INNER JOIN screenshots s ON s.id = cs.screenshot_id
        WHERE cs.run_name = %s AND cs.k_value = %s
        ORDER BY cs.cluster_id, cs.screenshot_id;
    """

    # load data into dataframe
    df = pd.read_sql(query, cnx, params=[run_name, k_value])

    # set source directory in image_path to source_path
    print(df)
    df["image_path"] = df["image_path"].map(
        lambda img_path: img_path.replace(
            "screenshots\\raw\\",
            source_path,
        )
    )

    # make dirs if not existing
    target_path = DATA_PATH / "datasets" / "json" / (f"k{k_value}") / filename
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    # export to dataset.json file
    with open(target_path, "w+") as json_file:
        files_list = df.values.tolist()
        dataset = {"labels": files_list}
        json.dump(dataset, json_file)

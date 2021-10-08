import json
import os
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import spacy
from dotenv import load_dotenv
from google.cloud.storage.bucket import Bucket
from pandas.core.frame import DataFrame
from spacy.language import Language
from spacy.pipeline import EntityRuler

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT")
DATA_PATH = Path(os.getenv("DATA_PATH"))
BUCKET_NAME = os.getenv("BUCKET_NAME")


def setup_pipeline(
    cloud_bucket: Bucket = None,
) -> Tuple[Language, dict, dict, dict, dict, DataFrame]:
    """Setup the spaCy pipeline for chatbot message nlp."""
    global nlp, intents, bucket

    # assign passed bucket obj, or None
    bucket = cloud_bucket

    # load pretrained model
    nlp = spacy.load("en_core_web_lg")

    # entity ruler config
    config = {
        "phrase_matcher_attr": None,
        "validate": False,
        "overwrite_ents": True,
        "ent_id_sep": "||",
    }

    # add entity ruler to pipeline
    entity_ruler = nlp.add_pipe("entity_ruler", config=config)

    # load patterns from disk or from bucket
    if cloud_bucket is None or ENVIRONMENT == "development":
        entity_ruler.from_disk(DATA_PATH / "chatbot" / "mapped_patterns.jsonl")
    else:
        patterns_path = "setup/mapped_patterns.jsonl"

        # download blob content from bucket
        blob = bucket.get_blob(patterns_path)
        patterns_list = blob.download_as_string().decode("utf-8").split("\r\n")

        # convert list of strs holding dicts into list of dicts
        patterns_dict_list = [json.loads(dict_str) for dict_str in patterns_list]

        entity_ruler.add_patterns(patterns_dict_list)

    # create second entity ruler for colors
    color_ruler = EntityRuler(nlp)

    # load patterns from disk or from bucket
    if cloud_bucket is None:
        color_ruler.from_disk(DATA_PATH / "chatbot" / "color_patterns.jsonl")
    else:

        color_patterns_path = "setup/color_patterns.jsonl"

        # download blob content from bucket
        blob = bucket.get_blob(color_patterns_path)
        color_list = blob.download_as_string().decode("utf-8").split("\r\n")

        # convert list of strs holding dicts into list of dicts
        colors_dict_list = [json.loads(dict_str) for dict_str in color_list]

        color_ruler.add_patterns(colors_dict_list)

    # add color patterns to entity ruler
    entity_ruler.add_patterns(color_ruler.patterns)

    # setup patterns for entity ruler
    patterns = entity_ruler.patterns

    # join patterns for similarity calculation and store in class variable
    # concat each token list for each pattern to string
    patterns = [
        {
            "label": pat["label"],
            "pattern": " ".join(
                list(map(lambda dct: list(dct.values())[0], pat["pattern"]))
            ),
            "id": pat["id"],
        }
        for pat in patterns
    ]
    print(f"Patterns setup completed: {str(len(patterns))}")

    if ENVIRONMENT == "production":
        # load from bucket
        intents = load_intents(use_bucket=True)
        answers = load_answers(use_bucket=True)
        hints = load_hints(use_bucket=True)
        rankings = load_rankings(use_bucket=True)
    else:
        # use file from local disk
        intents = load_intents(use_bucket=False)
        answers = load_answers(use_bucket=False)
        hints = load_hints(use_bucket=False)
        rankings = load_rankings(use_bucket=False)
    print(intents)
    print(nlp.pipeline)
    return (nlp, intents, patterns, answers, hints, rankings)


def load_intents(use_bucket: bool) -> Optional[Dict[str, Dict[str, Any]]]:
    """Load the intents for the classifier from `intents.json`.

    Args:
        use_bucket (bool): use_bucket (bool): if True use gcloud bucket, else file system

    Returns:
        List[Dict[str, List[str]]]: List of intents
    """
    intents = None

    if use_bucket:
        intents_path = "setup/intents.json"

        # download blob content from bucket
        blob = bucket.get_blob(intents_path)
        json_data = blob.download_as_string()

        intents = json.loads(json_data)
    else:
        intents_path = DATA_PATH / "chatbot" / "intents.json"

        # read json and return list of intents
        with open(intents_path, "r") as f:
            intents = json.loads(f.read())

    return intents


def load_answers(use_bucket: bool) -> Optional[Dict[str, Dict[str, List[str]]]]:
    """Load the answers from `answers.json`.

    Args:
        use_bucket (bool): use_bucket (bool): if True use gcloud bucket, else file system

    Returns:
        Optional[Dict[str, Dict[str, List[str]]]]: Dict with list of answers for each intent and each intent state. See `answers.json` for structure.
    """
    answers = None

    if use_bucket:
        answers_path = "setup/answers.json"

        # download blob content from bucket
        blob = bucket.get_blob(answers_path)
        json_data = blob.download_as_string()

        answers = json.loads(json_data)
    else:
        answers_path = DATA_PATH / "chatbot" / "answers.json"

        # read json and convert to dict
        with open(answers_path, "r") as f:
            answers = json.loads(f.read())

    return answers


def load_hints(use_bucket: bool) -> Optional[Dict[str, Dict[str, List[str]]]]:
    """Load the hints from `hints.json`.

    Args:
        use_bucket (bool): use_bucket (bool): if True use gcloud bucket, else file system

    Returns:
        Optional[Dict[str, Dict[str, List[str]]]]: Dict with list of hints for each intent and each intent state. See `hints.json` for structure.
    """
    hints = None
    if use_bucket:
        hints_path = "setup/hints.json"

        # download blob content from bucket
        blob = bucket.get_blob(hints_path)
        json_data = blob.download_as_string()

        hints = json.loads(json_data)
    else:
        hints_path = DATA_PATH / "chatbot" / "hints.json"

        # read json and convert to dict
        with open(hints_path, "r") as f:
            hints = json.loads(f.read())

    return hints


def load_rankings(use_bucket: bool) -> Optional[DataFrame]:
    """Load rankings for clusters from csv file.

    Args:
        use_bucket (bool): use_bucket (bool): if True use gcloud bucket, else file system

    Returns:
        DataFrame: rankings with cols [cluster_id, cluster_rank, label_name, factor_lf_ilf]
    """

    try:
        df = None
        if use_bucket:
            # rankings_path = "setup/rankings_k55_all.csv"
            rankings_path = "setup/rankings.csv"

            # download blob content from bucket
            blob = bucket.get_blob(rankings_path)

            # get bytestr from blob + convert to regular string
            csv_str = blob.download_as_string().decode("utf-8")

            # convert str into readable buffer
            csv_file = StringIO(csv_str)
        else:
            csv_file = DATA_PATH / "chatbot" / "rankings.csv"

        # load from existing rankings file
        df = pd.read_csv(csv_file)

        # filter all entries below threshold
        df = df[df["factor_lf_ilf"] >= 0.01]
    except Exception as e:
        # exit app
        print(e)
        print("df for rankings uninitialized")
        exit(1)
    return df

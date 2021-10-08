import csv
import logging
import os
from pathlib import Path

from mysql.connector import Error
from src.database.db_connector import (
    connect_to_mysql_server,
    create_database,
    create_table,
    get_connection_cursor,
    insert_label,
)

from ..schemas.label import Label
from .db_config import DATABASES

log = logging.getLogger("db")

cnx = None
cursor = None


def init_db(db_name: str, load_labels: bool = False):
    """Initializes the specified database.

    Args:
        db_name (str): name of the database
        load_labels (bool, optional): specifies if labels should be loaded from csv. Defaults to False.
    """
    # connection errors crash program
    global cnx, cursor
    cnx = connect_to_mysql_server()
    cursor = get_connection_cursor(cnx)

    # create new db without data
    try:
        create_database(db_name, cnx)
    except Error as err:
        log.error(f"Error while creating database {db_name}: {err.msg}")

    # add missing tables, existing tables are skipped
    try:
        TABLES = DATABASES[db_name]
        if TABLES is None:
            raise Exception("TABLES is None")
    except Exception:
        log.critical(
            f"Missing db configuration in db_config.py for {db_name}, exiting program"
        )
        exit(1)

    for table_name in TABLES:
        try:
            log.info(f"Creating table {table_name}...")
            create_table(db_name, TABLES[table_name], cursor)
        except Error as err:
            log.error(f"Error while creating table {table_name}: {err.msg}")

    log.info(f"{db_name} initialized.")

    # load labels if wanted
    if load_labels:
        db_load_labels(db_name)

    cursor.close()
    cnx.close()
    log.info("Closing connection")


def db_load_labels(db_name: str):
    """Loads labels from 'data/labels/labels.csv' into the specified database.

    Args:
        db_name (str): the database
    """
    log.info(f"Loading labels into {db_name}...")

    # get labels.csv
    data_path = os.getenv("DATA_PATH")
    labels_path = str(Path(data_path) / "labels" / "labels.csv")

    skipped_labels = []

    with open(labels_path) as labels_csv_file:
        labelsreader = csv.reader(labels_csv_file)
        labels = map(lambda row: Label(row[0], row[1], row[2]), labelsreader)

        # insert each label
        for label in labels:
            try:
                insert_label(db_name, label, cursor)
            except Error as err:
                log.error(err)
                skipped_labels.append(label)
            else:
                log.info(f"Inserted label {label}.")

    log.info(
        f"Loading labels completed. Skipped {len(skipped_labels)} labels: {list(map(lambda lb: lb.name, skipped_labels))}"
    )
    cnx.commit()


def format_labels_csv():
    """Format raw label data with format (name,category,href) in "labels_raw.csv" and store it as (name,category,href) in "labels.csv"."""
    data_path = os.getenv("DATA_PATH")
    labels_raw_path = str(Path(data_path) / "labels" / "labels_raw.csv")
    labels_path = str(Path(data_path) / "labels" / "labels.csv")

    with open(labels_raw_path) as labels_raw_csv_file:
        # read raw label data
        labels_raw_reader = csv.reader(labels_raw_csv_file)

        with open(labels_path, "w", newline="") as labels_csv_file:
            labels_writer = csv.writer(labels_csv_file)

            for label in labels_raw_reader:
                label_name = label[0]
                label_type = label[1].lower()

                # check if href was supplied
                label_href = None
                try:
                    label_href = label[2]
                except Exception as err:
                    log.error(f"No href supplied for {label_name}")

                if label_href is None:
                    # no href has been supplied
                    label_href = label_name

                if not label_type == "country":
                    # format href
                    label_href = (
                        label_href.lower()
                        .replace(" / ", "-")
                        .replace(" & ", "-")
                        .replace(" - ", "-")
                        .replace(" ", "-")
                        .replace(".", "-")
                    )

                # write formatted label
                log.info(f"Writing row: ({label_name}, {label_type}, {label_href})")
                labels_writer.writerow([label_name, label_type, label_href])


def db_disable_strict_mode(db_name: str):
    # SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';
    # SELECT @@GLOBAL.sql_mode;
    raise NotImplementedError

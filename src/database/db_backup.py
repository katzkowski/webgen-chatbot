import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

log = logging.getLogger("db_backup")

load_dotenv()

BACKUP_PATH = os.getenv("BACKUP_PATH")
MYSQLDUMP_PATH = os.getenv("MYSQLDUMP_PATH")


def create_db_backup(db_name: str):
    """Creates a backup using mysqldump of the specified database

    Args:
        db_name (str): the database to backup

    Raises:
        Exception: unknown exception during execution
    """
    log.info(f"Creating backup for database {db_name}")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    try:
        process = subprocess.run(
            [
                MYSQLDUMP_PATH,
                "-e",
                "--user",
                "root",
                "--password",
                "--host",
                "localhost",
                "--port",
                "1008",
                db_name,
                "--result-file",
                f"{BACKUP_PATH}\dump_{db_name}_{timestamp}.sql",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as err:
        log.error(f"Creating db backup failed: {err}")
        raise err
    else:
        log.info(f"Created backup at '{BACKUP_PATH}\dump_{db_name}_{timestamp}.sql'")

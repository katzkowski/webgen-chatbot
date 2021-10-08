import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from dotenv import load_dotenv
from PIL import ImageFile

from ..database.db_connector import (
    connect_to_database,
    delete_screenshot,
    get_connection_cursor,
    use_database,
)

load_dotenv()
log = logging.getLogger("dataset")

cnx = None
db_cursor = None


def find_truncated_screenshots() -> List[str]:
    """Returns a list of truncated screenshot files found in at 'data/screenshots/raw'.

    Returns:
        List[str]: list of truncated screenshot files
    """
    PATH = Path(os.getenv("DATA_PATH")) / "screenshots" / "raw"

    truncated_screenshots = []

    for filename in os.listdir(PATH):
        try:
            # fail if file is truncated
            im = ImageFile.Image.open(PATH / filename)
            im.convert("RGB")
        except OSError:
            log.info(f"Found truncated screenshot at {str(PATH / filename)}")
            truncated_screenshots.append(filename)

    log.info(f"Found {len(truncated_screenshots)} truncated screenshots")
    return truncated_screenshots


def get_truncated_screenshots_ids() -> List[Optional[int]]:
    """Returns a list of truncated screenshot ids based on files at 'data/screenshots/truncated'.

    Returns:
       List[Optional[int]]: list of truncated screenshot ids
    """
    TRUNCATED_PATH = Path(os.getenv("DATA_PATH")) / "screenshots" / "truncated"
    truncated_screenshots = os.listdir(TRUNCATED_PATH)
    log.info(f"Getting ids for {len(truncated_screenshots)} truncated screenshots")

    # get ids of screenshots to be removed
    for idx, filename in enumerate(truncated_screenshots):
        # image_path value stored in db
        image_path = "screenshots\\raw\\" + filename
        log.info(f"Querying id for screenshot {filename}")

        query = """
            SELECT id FROM screenshots 
            WHERE image_path=%s;
        """

        # get id of screenshot
        try:
            db_cursor.execute(query, (image_path,))
            screenshot_id = db_cursor.fetchone()
        except Exception as err:
            log.error(
                f"Failed retrieving id for screenshot with image_path {image_path}: {err}"
            )
            log.info(f"Skipping screenshot with image_path {image_path}")
            continue

        if screenshot_id:
            truncated_screenshots[idx] = screenshot_id[0]
            log.info(f"Retrieved id for screenshot with image_path {image_path}")
        else:
            truncated_screenshots[idx] = None
            log.info(f"No result for screenshot with image_path {image_path}")

    return truncated_screenshots


def remove_truncated_screenshots_from_db(db_name: str) -> None:
    global cnx, db_cursor

    # intentionally without try-except to crash program
    cnx = connect_to_database(db_name)
    db_cursor = get_connection_cursor(cnx)
    use_database(db_name, db_cursor)

    truncated_ids = get_truncated_screenshots_ids()

    log.info(
        f"Removing {len(truncated_ids)} truncated screenshots from database {db_name}"
    )

    skipped_screenshots = []

    # remove screenshots from database
    for screenshot_id in truncated_ids:
        try:
            delete_screenshot(db_name, screenshot_id, db_cursor)
            cnx.commit()
        except Exception as err:
            log.warning(f"Skipping screenshot with id {screenshot_id}")
            skipped_screenshots.append(screenshot_id)
            cnx.rollback()
            continue

    if skipped_screenshots:
        log.warning(
            f"Skipped {len(skipped_screenshots)} screenshots: {skipped_screenshots}"
        )

    log.info(
        f"Removed {len(truncated_ids) - len(skipped_screenshots)} screenshots from database {db_name}"
    )

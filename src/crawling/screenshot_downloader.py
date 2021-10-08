import logging
import os
from pathlib import Path
from time import sleep
from typing import Optional

import requests
from PIL import Image
from requests.exceptions import HTTPError, RequestException, Timeout, TooManyRedirects

from ..database import db_connector as db
from ..schemas.screenshot import Screenshot
from ..schemas.website import Website
from ..scraping.url_scraper import UrlScraper
from ..scraping.website_scraper import WebsiteScraper

log = logging.getLogger("downloader")

# time to wait before starting a new request in seconds
SERVER_REQUEST_DELAY = 5

DATA_PATH = os.getenv("DATA_PATH")
db_name = "crawling_db"
cnx = None
cursor = None
downloadable_screenshots = []
skipped_screenshots = []


def init_downloader():
    """Initalizes the screenshot downloader."""
    global db_name, cnx, cursor, downloadable_screenshots, DATA_PATH

    log.info("Connecting to database")
    try:
        cnx = db.connect_to_database(db_name)
        cursor = db.get_connection_cursor(cnx)
        log.info("Connected to database")
    except Exception as err:
        log.critical(f"Connecting to database failed: {err}")
        log.info("Exiting program")
        exit(1)

    # get all (downloadable) screenshots from database
    log.info("Checking database for downloadable screenshots")
    try:
        query = """
            SELECT * FROM screenshots;
        """
        # SELECT * FROM screenshots WHERE image_path IS NULL;
        cursor.execute(query)
    except Exception as err:
        log.critical(f"Retrieving screenshot data failed: {err}")
        log.info("Exiting program")
        exit(1)

    # fetch results
    try:
        downloadable_screenshots = cursor.fetchall()
    except Exception as err:
        log.critical(f"Error while fetching screenshots from cursor: {err}")
        log.info("Exiting program")
        exit(1)

    no_screenshots = len(downloadable_screenshots)
    if no_screenshots == 0:
        log.warning(
            f"Fetched {len(downloadable_screenshots)} downloadable screenshots from database"
        )
    else:
        log.info(
            f"Fetched {len(downloadable_screenshots)} downloadable screenshots from database"
        )

    # check target directory
    screenshots_path = Path(DATA_PATH) / "screenshots" / "raw"

    if not screenshots_path.is_dir():
        log.critical("Screenshots data path is not a directory or does not exist")
        log.info("Exiting program")
        exit(1)
    else:
        log.info(f"Path to screenshot data is {screenshots_path}")
        log.info("Downloader initialized")


def run_downloader():
    """Run the screenshot downloader."""
    global DATA_PATH
    init_downloader()

    log.info("Running downloader")
    scr_counter = 0

    for row in downloadable_screenshots:
        # create screenshot object from database row
        scr = Screenshot(row[1], row[2], row[3], row[4], row[5], row[6])

        # validate screenshot object
        try:
            scr.validate()
        except Exception as err:
            log.error(
                f"Error while validating screenshot with url {scr.img_url}: {err}"
            )
            log.info(f"Skipping screenshot with url {scr.img_url}")
            skipped_screenshots.append(scr)
            continue
        else:
            file_name = scr.img_url.split("/")[-1]

            # relative path to data root dir
            scr_relative_path = Path("screenshots") / "raw" / file_name

            # absolute path
            scr_absolute_path = Path(DATA_PATH) / scr_relative_path

            # check if file at target path already exists
            if scr_absolute_path.is_file():
                log.info(f"Already downloaded screenshot with url {scr.img_url}")
                continue

            # download file from url
            scr_bytes = download_screenshot(scr)

            # if download was unsuccessful
            if scr_bytes is None:
                log.info(f"Skipping screenshot with url {scr.img_url}")
                skipped_screenshots.append(scr)
                continue

            # store screenshot on disk and reference path in db
            store_screenshot(scr, scr_bytes, scr_absolute_path, scr_relative_path)
            scr_counter += 1

    log.info(f"Skipped {len(skipped_screenshots)} screenshots")
    log.info(f"Downloaded {scr_counter} screenshots")


def download_screenshot(screenshot: Screenshot) -> Optional[bytes]:
    """Downloads the specified screenshot from its url.

    Args:
        screenshot (Screenshot): the screenshot

    Returns:
        Optional[bytes]: byte object of screenshot
    """

    # validate file extension
    file_extension = screenshot.img_url.split(".")[-1].lower()
    if not (
        file_extension != "jpg" or file_extension != "jpeg" or file_extension != "png"
    ):
        log.warning(f"Invalid file extension '.{file_extension}'")
        return None

    sleep(SERVER_REQUEST_DELAY)

    # get screenshot from url
    log.info(f"Retrieving {screenshot.img_url}")
    try:
        response = requests.get(screenshot.img_url, timeout=5)
        response.raise_for_status()
    except HTTPError as err:
        log.error(
            f"HTTPError: screenshot with url {screenshot.img_url}, status code {response.status_code}"
        )

        return None
    except Timeout as err:
        log.error(f"Timeout: screenshot with url {screenshot.img_url}")
        return None
    except TooManyRedirects as err:
        log.error(f"TooManyRedirects: screenshot with url {screenshot.img_url}")
        return None
    except RequestException as err:
        log.error(f"RequestException: screenshot with url {screenshot.img_url}")
        return None
    except Exception as err:
        log.error(f"Unknown exception: screenshot with url {screenshot.img_url}: {err}")
        return None

    # check for valid response
    if not response.ok:
        log.error(
            f"Response status code not 'ok': screenshot with url {screenshot.img_url}"
        )
        return None

    # screenshot bytes
    return response.content


def store_screenshot(
    scr: Screenshot,
    screenshot_bytes: bytes,
    abs_target_path: Path,
    rel_target_path: Path,
) -> None:
    """Stores the specified screenshot by writing the byte object to the target path.

    Args:
        scr (Screenshot): screenshot object of screenshot
        screenshot_bytes (bytes): byte object of screenshot
        abs_target_path (Path): absolute path to write file at
        rel_target_path (Path): relative path to store in db
    """
    #  store file
    with open(abs_target_path, "wb") as handler:
        # write file from byte object
        try:
            handler.write(screenshot_bytes)
        except Exception as err:
            log.error(
                f"Exception while writing file for screenshot with url {scr.img_url}: {err}"
            )
            log.info(f"Skipping screenshot with url {scr.img_url}")
            skipped_screenshots.append(scr)
            return None

    # get file_size
    file_size = None
    try:
        file_size = os.path.getsize(abs_target_path)
    except Exception as err:
        log.warning(
            f"Exception while retrieving file size of screenshot with url {scr.img_url}: {err}"
        )

    # get dimensions
    (dimension_x, dimension_y) = (None, None)
    try:
        (dimension_x, dimension_y) = Image.open(abs_target_path).size
    except Exception as err:
        log.warning(
            f"Exception while retrieving dimensions (x,y) of screenshot with url {scr.img_url}: {err}"
        )

    # update db with path, size, dimensions
    try:
        query = """
            UPDATE screenshots
            SET image_path = %s, image_size = %s, dimension_x = %s, dimension_y = %s
            WHERE image_url = %s;
        """
        cursor.execute(
            query,
            (
                str(rel_target_path),
                file_size,
                dimension_x,
                dimension_y,
                scr.img_url,
            ),
        )
    except Exception as err:
        log.error(f"Updating screenshot with url {scr.img_url} failed: {err}")
        cnx.rollback()
    else:
        log.info(f"Screenshot with url {scr.img_url} updated successfully.")
        cnx.commit()

import logging
from time import sleep
from typing import List

from requests.exceptions import HTTPError

from ..database import db_connector as db
from ..schemas.label import Label
from ..schemas.website import Website
from ..scraping.url_scraper import UrlScraper
from ..scraping.website_scraper import WebsiteScraper

log = logging.getLogger("crawler")

# time to wait before starting a new request in seconds
SERVER_REQUEST_DELAY = 5

db_name = None
cnx = None
cursor = None
labels = []
unknown_labels = set()

# url to append website hrefs to
base_url = "https://www.awwwards.com"


def init_crawler():
    """Initialize the crawling process."""
    global db_name, cnx, cursor, labels
    db_name = "crawling_db"

    log.info("Initializing crawler")

    log.info("Connecting to database")
    try:
        cnx = db.connect_to_mysql_server()
        cursor = db.get_connection_cursor(cnx)
    except Exception as err:
        log.critical(f"Connecting to database failed: {err}")
        log.info("Exiting program")
        exit(1)

    log.info("Retrieving labels")
    try:
        labels = db.get_all_labels(db_name, cursor)
    except Exception as err:
        log.critical(f"Retrieving labels failed: {err}")
        log.info("Exiting program")
        exit(1)

    log.info(f"Retrieved {len(labels)} labels")

    log.info("Crawler initialized")


def run_crawler(labels_start_index: int = 0):
    """Run the crawling process"""
    global unknown_labels
    init_crawler()

    log.info("Running crawler")

    for label in labels[labels_start_index:]:
        crawl_label(label, 1)

    log.info(f"Encountered {len(unknown_labels)} unknown labels: {unknown_labels}")
    log.info("Crawling finished")


def crawl_label(label: Label, page_no: int):
    """Crawl a specific page for a label and start scraping website data.

    Args:
        label (Label): the label to crawl websites for
        page_no (int): the results page number
    """

    log.info(f"Crawling label {label.name} on page {page_no}")

    if page_no > 350:
        # abort label crawling
        log.warn(f"Page limit 350 exceeded: aborting crawl for label {label.name}")
        return

    # scrape label page
    try:
        # create new url scraper
        url_scraper = UrlScraper(label, page_no, "nominees")
    except HTTPError as err:
        if err.response.status_code == 404:
            # exceeded last content page
            log.error(f"404 error on page {page_no} for {label.name}")
            log.info(f"Finished crawling label {label}")
            return None
        else:
            # unknown error, stop crawling for label
            log.error(f"Error on page {page_no} for {label.name}: {err}")
            log.info(f"Finished crawling label {label}")
            return None
    except Exception as err:
        # unknown error, stop crawling for label
        log.error(f"Error on page {page_no} for {label.name}: {err}")
        log.info(f"Finished crawling label {label}")
        return None

    # get urls from label page
    urls = None
    try:
        urls = url_scraper.get_website_urls()
    except Exception as err:
        log.error(f"Error on page {page_no} for {label.name}: {err}")

    if urls is None:
        # unknown exception occured while getting urls, try next page
        crawl_label(label, (page_no + 1))
    elif len(urls) == 0:
        # exceeded last content page
        log.info(f"Exceeded last content page on page {page_no} for label {label.name}")
        log.info(f"Finished crawling label {label}")
        return None
    else:
        log.info(f"Scraping {len(urls)} websites from {label} page {page_no}")
        scrape_websites(urls)

        # continue with next page for label
        sleep(SERVER_REQUEST_DELAY)
        crawl_label(label, (page_no + 1))
        log.info("Continuing with next website")


def scrape_websites(urls: List[str]):
    """Scrape over a list of urls and store them in database with labels and screenshots.

    Args:
        urls ([str]): list of website urls
    """
    for url in list(map(lambda href: base_url + href, urls)):

        # check if website is already stored
        try:
            stored = db.get_website_by_url(db_name, url, cursor)
        except Exception as err:
            log.error(f"Checking if website {url} is stored failed: {err}")
            log.info(f"Skipping website {url}")
            continue

        if stored is not None:
            log.warn(f"Website {url} already stored")
            log.info(f"Skipping website {url}")
            continue

        sleep(SERVER_REQUEST_DELAY)

        # create new website scraper
        try:
            scraper = WebsiteScraper(url)
        except Exception as err:
            # unknown error, skip
            log.error(f"Scraping website at {url} failed: {err}")
            log.info(f"Skipping website {url}")
            continue

        # scrape website
        try:
            website = scraper.get_page_data()
        except Exception as err:
            # unknown error, skip
            log.error(f"Getting website data at {url} failed: {err}")
            log.info(f"Skipping website {url}")
            continue

        # insert website into db
        try:
            db.insert_website(db_name, website, cursor)
        except Exception as err:
            log.error(f"Inserting website {url} into db failed: {err}")
            log.info(f"Rolling transaction back for website {url}")
            cnx.rollback()
            log.info(f"Skipping website {url}")
            continue

        # commit website
        cnx.commit()

        # get website id
        try:
            website_id = db.get_website_by_url(db_name, website.url, cursor)[0]
        except Exception as err:
            log.error(f"Getting website_id of '{website.title}'' failed: {err}")
            log.info(f"Skipping website {url}")
            continue

        skipped_screenshots = 0

        # insert screenshots
        for screenshot in website.screenshots:
            try:
                db.insert_screenshot(db_name, screenshot, cursor)
            except Exception as err:
                log.error(
                    f"Inserting screenshot {screenshot.img_url} of website '{website.title}' failed: {err}"
                )
                log.info(f"Skipping screenshot {screenshot.img_url}")
                skipped_screenshots += 1
                continue

        if skipped_screenshots == len(website.screenshots):
            # if no screenshot was inserted
            log.warn(f"No screenshots inserted for website {url}")
            log.info(f"Rolling transaction back for all screenshots of website {url}")
            log.info(f"Continuing with next website")
            cnx.rollback()
            continue
        elif skipped_screenshots != 0:
            log.warn(
                f"Skipped {skipped_screenshots} out of {len(website.screenshots)} screenshots for website {url}"
            )

        global unknown_labels
        skipped_labels = 0

        # insert website_labels
        for label_href in website.labels:
            # get label id
            try:
                (label_id, label) = db.get_label_by_href(db_name, label_href, cursor)
            except Exception as err:
                log.error(f"Retrieving label_id of {label_href} failed: {err}")
                log.info(f"Skipping label {label_href}")
                skipped_labels += 1
                unknown_labels.add(label_href)
                continue

            # insert website_label
            try:
                db.insert_website_label(db_name, website_id, label_id, cursor)
            except Exception as err:
                log.error(
                    f"Inserting label {label.name} of website {website.title} failed: {err}"
                )
                log.info(f"Skipping label {label.name}")
                skipped_labels += 1
                continue

        if skipped_labels == len(website.labels):
            # if no label was inserted
            log.warn(f"No labels inserted for website {url}")
            log.info(
                f"Rolling transaction back for all screenshots and labels of website {url}"
            )
            log.info(f"Continuing with next website")
            cnx.rollback()
            continue
        elif skipped_labels != 0:
            log.warn(
                f"Skipped {skipped_labels} out of {len(website.labels)} labels for website {url}"
            )

        # commit transaction
        cnx.commit()
        log.info(f"Transaction for screenshots and labels website {url} commited.")

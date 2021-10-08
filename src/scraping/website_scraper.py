import logging
import re
from typing import List

from bs4 import BeautifulSoup
from src.schemas.screenshot import Screenshot
from src.schemas.website import Website

from .scraper import Scraper

log = logging.getLogger("scraper")


class WebsiteScraper(Scraper):
    """Scrapes a single page that presents a website from awwwards.com."""

    def __init__(self, website_url: str) -> None:
        super().__init__(website_url)
        self.page_type = self.get_page_type()
        self.page_title = self.get_page_title()

    def __str__(self) -> str:
        return f"WebsiteScraper({self.page_title}, {self.url}, page type: {self.page_type})"

    def get_page_type(self) -> str:
        """Returns the type of the page: 'w' for winner, 'n' for nominee.

        Raises:
            AttributeError: raised by BeautifulSoup.find()
            Exception:  Invalid page type
                        Unknown exception

        Returns:
            str: 'w' or 'n'
        """
        try:
            # search for nominee page element
            nominee = self.bs4_html.find("div", {"class": "box-breadcrumb"}).find(
                "a", {"href": "/nominees/"}
            )

            # return if nominee found
            if nominee != None:
                return "n"
            else:
                # search for winner page element
                winner = self.bs4_html.find("div", {"class": "box-breadcrumb"}).find(
                    "a", {"href": "/awards-of-the-day/"}
                )

                # return if winner found
                if winner != None:
                    return "w"
                else:
                    raise Exception(
                        f"Invalid page type: get_page_type() for {self.url}"
                    )
        except AttributeError as err:
            log.error(f"AttributeError: get_page_type() for {self.url}")
            raise err
        except Exception as err:
            log.error(f"Unknown Exception: get_page_type() for {self.url}: {err}")
            raise err

    def get_page_screenshots(self) -> List[Screenshot]:
        """Returns a list of website screenshots presented on the page.

        Returns:
            List[Screenshot]: list of screenshots
        """
        if self.page_type == "n":
            # lazy-loaded img inside box-screenshot div
            img = self.bs4_html.find("div", {"class": "box-screenshot"}).find(
                "img", {"class": ["lazy", "lazy-loaded"]}
            )

            screenshots = []
            try:
                screenshots.append(
                    Screenshot(
                        self.url,
                        img["data-src"],
                        None,
                        None,
                        int(img["width"]),
                        int(img["height"]),
                    )
                )
                return screenshots
            except TypeError as err:
                log.warning(
                    f"Skipping screenshot: TypeError: get_page_screenshots() for {self.url}"
                )
                raise err
            except Exception as err:
                log.warning(
                    f"Skipping screenshot: Unknown Exception: get_website_screenshot() for {self.url}: {err}"
                )
                raise err
        elif self.page_type == "w":
            # first content-view block div
            content_block = self.bs4_html.find("div", {"class": "content-view"}).find(
                "div", class_="block pt-0"
            )

            # lazy-loaded img inside first four box-photo divs
            imgs = list(
                map(
                    lambda div: div.find("img", {"class": ["lazy", "lazy-loaded"]}),
                    content_block.find_all("div", {"class": "box-photo"}, limit=4),
                )
            )

            # extract all screenshots from winner page
            screenshots = []
            for img in imgs:
                try:
                    screenshot = Screenshot(self.url, img["data-src"])
                except TypeError as err:
                    log.warning(
                        f"Skipping screenshot: TypeError: get_page_screenshots() for {self.url}"
                    )
                    continue
                except Exception as err:
                    log.warning(
                        f"Skipping screenshot: Unknown Exception: get_page_screenshots() for {self.url}: {err}"
                    )
                    continue

                if screenshot != None:
                    screenshots.append(screenshot)

            return screenshots
        else:
            raise Exception(f"Invalid page type: get_page_screenshots() for {self.url}")

    def get_page_labels(self) -> List[str]:
        """Returns a list of labels for the presented website.

        Raises:
            Exception: unknown exception

        Returns:
            List[str]: list of labels
        """
        try:
            # list of li elements with tags
            ul_tags = self.bs4_html.find("div", {"class": "list-tags"}).ul.find_all(
                "li"
            )

            labels = []
            for li in ul_tags:
                # extract tag name from href attribute
                tag_name = re.search("/websites/(.+?)/", li.a["href"]).group(1)
                labels.append(tag_name)
            return labels
        except Exception as err:
            log.error(f"Unknown Exception: get_page_labels() for {self.url}: {err}")
            raise err

    def get_page_title(self) -> str:
        """Returns the title of the page.

        Raises:
            Exception: unknown exception

        Returns:
            str: page title
        """
        try:
            title = self.bs4_html.title.get_text()
            title_pattern = re.compile(" - Awwwards")

            # extract website name from Awwwards page title
            title_end = title_pattern.search(title).start()
            return title[:title_end]
        except Exception as err:
            log.error(f"Unknown Exception: get_page_title() for {self.url}: {err}")
            raise err

    def get_page_data(self) -> Website:
        """Returns all data of the scraped page as a Website object.

        Raises:
            Exception: unknown exception

        Returns:
            Website: scraped website data
        """
        try:
            log.info(f"Getting website data for {self.url}")
            return Website(
                self.page_title,
                self.url,
                self.page_type,
                "awwwards",
                self.get_page_screenshots(),
                self.get_page_labels(),
                self.bs4_html,
            )
        except Exception as err:
            log.error(f"Unknown Exception: get_page_data() for {self.url}")
            raise err

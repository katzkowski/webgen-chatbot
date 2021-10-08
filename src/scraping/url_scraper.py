import logging
from typing import List

from bs4 import BeautifulSoup
from src.schemas.label import Label

from .scraper import Scraper

log = logging.getLogger("scraper")


class UrlScraper(Scraper):
    """Scrapes a Label site for links to presenting websites."""

    def __init__(self, label: Label, page_no: int, award_type: str = None) -> None:
        self.label = label
        self.page_no = page_no
        self.award_type = award_type

        # if an award type was specified
        if isinstance(self.award_type, str):
            target_url = f"https://www.awwwards.com/websites/?award={self.award_type}&{self.label.label_type}={self.label.href}&page={self.page_no}"
        else:
            target_url = f"https://www.awwwards.com/websites/{self.label.href}/?page={self.page_no}"
        super().__init__(target_url)

    def __str__(self) -> str:
        return f"UrlScraper({self.label.name}, {self.url}, page no. {self.page_no})"

    def get_website_urls(self) -> List[str]:
        """Returns a list of urls to websites presented on current site.

        Raises:
            Exception: unknown exception

        Returns:
            List[str]: list of urls
        """
        try:
            # get website items
            ul = self.bs4_html.find("ul", {"class": "js-elements-container"})
            lis = ul.find_all("li", {"class": "js-collectable"})
        except Exception as err:
            log.error(
                f"Unknown Exception: get_website_urls() for {self.url} on page {self.page_no}: {err}"
            )
            raise err

        # get urls from items
        urls = []
        for li in lis:
            try:
                url = li.find("a")["href"]
                log.info(f"Found url {url}")
                urls.append(url)
            except Exception as err:
                log.warning(
                    f"Skipping url in get_website_urls() for {self.url} on page {self.page_no}: {err}"
                )

        log.info(f"Collected {len(urls)} urls from {self.url}")

        # more urls than maximum presented websites collected
        if len(urls) > 36:
            log.warning(
                f"Collected urls from get_website_urls() for {self.url} on page {self.page_no} could be polluted."
            )

        return urls

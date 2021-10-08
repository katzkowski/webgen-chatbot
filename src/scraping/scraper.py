import logging

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, RequestException, Timeout, TooManyRedirects

log = logging.getLogger("scraper")


class Scraper:
    """Base class for scraper with minimum functionality."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.bs4_html = self.get_page_html()

    def __str__(self) -> str:
        return f"Scraper({self.url})"

    def get_page_html(self) -> BeautifulSoup:
        """Returns a BeautifulSoup object of the specified url.

        Raises:
            HTTPError: http.get() return unsuccessful status code
            Timeout: http.get() timed out
            TooManyRedirects: too many redirects during http.get()
            RequestException: exception during http.get()
            Exception: unknown exception

        Returns:
            BeautifulSoup: parsed object of html of url
        """
        log.info(f"Retrieving {self.url}")
        try:
            html = requests.get(self.url, timeout=5)
            html.raise_for_status()
            return BeautifulSoup(html.content, "html.parser")
        except HTTPError as err:
            log.error(
                f"HTTPError: get_page_html() for {self.url}, status code {html.status_code}"
            )
            raise err
        except Timeout as err:
            log.error(f"Timeout: get_page_html() for {self.url}.")
            raise err
        except TooManyRedirects as err:
            log.error(f"TooManyRedirects: get_page_html() for {self.url}")
            raise err
        except RequestException as err:
            log.error(f"RequestException: get_page_html() for {self.url}")
            raise err
        except Exception as err:
            log.error(f"Unknown exception: get_page_html() for {self.url}: {err}")
            raise err

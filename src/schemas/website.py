import re
from typing import List

from bs4 import BeautifulSoup

from .screenshot import Screenshot

website_url_pattern = re.compile("https://www\.awwwards\.com/sites/")


class Website:
    """
    Represents a scraped website.
    """

    def __init__(
        self,
        title: str,
        url: str,
        page_type: str,
        scraped_from: str,
        screenshots: List[Screenshot] = None,
        labels: List[str] = None,
        html: BeautifulSoup = None,
    ) -> None:
        self.title = title
        self.url = url
        self.page_type = page_type
        self.scraped_from = scraped_from
        self.screenshots = screenshots
        self.labels = labels
        self.html = html

    def __str__(self) -> str:
        screenshots_str_list = list(map(lambda s: str(s), self.screenshots))
        return f"from {self.scraped_from}: {self.title}, {self.url}, type: {self.page_type}\ntags: {self.labels}\nscreenshots: {screenshots_str_list}"

    def validate(self):
        """Validates the website for MySQL database. Website is valid, if no error is raised.

        Raises:
            TypeError:  Invalid website title type
                        Invalid website url type
                        Invalid website page_type type
            ValueError: Invalid website title length
                        Invalid website url length
                        Invalid website url pattern
                        Invalid website page_type length
                        Invalid website page_type pattern
                        Invalid website scraped_from field length
                        Website has no labels
                        Website has no screenshots
        """
        if not isinstance(self.title, str):
            raise TypeError("Invalid website title type.")

        if not len(self.title) <= 255:
            raise ValueError("Invalid website title length.")

        if not isinstance(self.url, str):
            raise TypeError("Invalid website url type.")

        if not len(self.url) <= 255:
            raise ValueError("Invalid website url length.")

        if not website_url_pattern.match(self.url):
            raise ValueError("Website url pattern mismatch.")

        if not isinstance(self.page_type, str):
            raise TypeError("Invalid website page_type type.")

        if not len(self.page_type) == 1:
            raise ValueError("Invalid website page_type length.")

        if not (re.compile("[nwNW]").match(self.page_type)):
            raise ValueError("Website page_type pattern mismatch.")

        if not isinstance(self.scraped_from, str):
            raise TypeError("Invalid website scraped_from type.")

        if not len(self.scraped_from) <= 255:
            raise ValueError("Invalid website scraped_from field length.")

        if self.labels is None or len(self.labels) == 0:
            raise ValueError("Website has no labels")

        if self.screenshots is None or len(self.screenshots) == 0:
            raise ValueError("Website has no screenshots")

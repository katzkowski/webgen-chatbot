import re


class Screenshot:
    """
    Represents a screenshot of a website.
    """

    def __init__(
        self,
        page_url: str,
        img_url: str,
        img_path: str = None,
        img_size: int = None,
        dimension_x: int = None,
        dimension_y: int = None,
    ) -> None:
        """
        Args:
            page_url (str): url of page image is from
            img_url (str): url of image
            img_path (str): file path on disk
            img_size (int): file size
            dimension_x (int): width in px
            dimension_y (int): height in px
        """
        self.page_url = page_url
        self.img_url = img_url
        self.img_path = img_path
        self.img_size = img_size
        self.dimension_x = dimension_x
        self.dimension_y = dimension_y

    def __str__(self) -> str:
        return f"Screenshot of page {self.page_url}, url: {self.img_url}, path: {self.img_path}, size: {self.img_size}, dimension_x: {self.dimension_x} px, dimension_y: {self.dimension_y} px"

    def validate(self):
        """Validates the screenshot for MySQL database. Screenshot is valid, if no error is raised.

        Raises:
            TypeError:  Invalid screenshot url type
                        Invalid screenshot path type
                        Invalid screenshot size type
                        Invalid screenshot dimension_x type
                        Invalid screenshot dimension_y type
            ValueError: Invalid screenshot url length
                        Screenshot url pattern mismatch
                        Invalid screenshot path length
        """
        if not isinstance(self.img_url, str):
            raise TypeError("Invalid screenshot url type.")

        if not len(self.img_url) <= 255:
            raise ValueError("Invalid screenshot url length.")

        screenshot_url_pattern = re.compile("https://assets\.awwwards\.com/")

        if not screenshot_url_pattern.match(self.img_url):
            raise ValueError("Screenshot url pattern mismatch.")

        if not isinstance(self.page_url, str):
            raise TypeError("Invalid screenshot page_url type.")

        if not len(self.page_url) <= 255:
            raise ValueError("Invalid screenshot page_url length.")

        website_url_pattern = re.compile("https://www\.awwwards\.com/sites/")

        if not website_url_pattern.match(self.page_url):
            raise ValueError("Screenshot page_url pattern mismatch.")

        if not (isinstance(self.img_path, str) or self.img_path is None):
            raise TypeError("Invalid screenshot path type.")

        if self.img_path is not None and not len(self.img_path) <= 255:
            raise ValueError("Invalid screenshot path length.")

        if not (isinstance(self.img_size, int) or self.img_size is None):
            raise TypeError("Invalid screenshot size type.")

        if not (isinstance(self.dimension_x, int) or self.dimension_x is None):
            raise TypeError("Invalid screenshot dimension_x type.")

        if not (isinstance(self.dimension_y, int) or self.dimension_y is None):
            raise TypeError("Invalid screenshot dimension_y type.")

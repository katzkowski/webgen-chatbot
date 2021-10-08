import unittest

from src.schemas.website import Website


class TestWebsite(unittest.TestCase):
    def setUp(self):
        self.too_long_string = "C7Thkl2AQpWemHiAPbEpeXr96r37X0PItQcs5qxiSx3zWT0dMJ5gA3NUvHjszCAXUUCinuVDGAcVDaX6INKyojuyxObhHudXGKBVD1a3A0MpjnINGt2pbPw0NqGqBPTUxIfrxfSeInkKIT4GimLC8IgtEjYgFGhaBuTbN3Fzj73yZ3FrcJVgyTeDRlgL2zMpOKed0YSMDQbLwLJ8lcLWc1SDGUImNpgsRpxf844M5fJmQg1exrH2gfd36qwb1OY3"
        # valid website
        self.website = Website(
            "Proxy",
            "https://www.awwwards.com/sites/proxy",
            "n",
            "awwwards",
            [
                "Screenshot from page https://www.awwwards.com/sites/proxy, url: https://assets.awwwards.com/awards/submissions/2021/04/608823823fff0615519193.png, path: None, size: None, dimension_x: 918 px, dimension_y: 656 px"
            ],
            [
                "technology",
                "web-interactive",
                "startups",
                "animation",
                "responsive-design",
                "storytelling",
                "interaction-design",
                "react",
                "gatsby",
                "framer-motion",
                "red",
            ],
            None,
        )

    def test_validate_valid_website(self):
        # valid website throws no exception
        self.website.validate()

    def test_validate_invalid_website_type(self):
        with self.assertRaises(TypeError):
            self.website.title = None
            self.website.validate()

    def test_validate_website_title_too_long(self):
        # website title too long (256 characters)
        with self.assertRaises(ValueError):
            self.website.title = self.too_long_string
            self.website.validate()

    def test_validate_invalid_url_tyle(self):
        # invalid url type
        with self.assertRaises(TypeError):
            self.website.url = None
            self.website.validate()

    def test_validate_website_url_too_long(self):
        # url too long (256 characters)
        with self.assertRaises(ValueError):
            self.website.url = self.too_long_string
            self.website.validate()

    def test_validate_website_url_pattern_mismatch(self):
        # url not matching patter
        with self.assertRaises(ValueError):
            self.website.url = "https://www.awwwards.com/academy/"
            self.website.validate()

    def test_validate_invalid_page_type(self):
        # invalid page_type
        with self.assertRaises(TypeError):
            self.website.page_type = None
            self.website.validate()

    def test_validate_page_type_too_short(self):
        # page_type too short (empty)
        with self.assertRaises(ValueError):
            self.website.page_type = ""
            self.website.validate()

    def test_validate_page_type_too_long(self):
        # page_type too long (2)
        with self.assertRaises(ValueError):
            self.website.page_type = "no"
            self.website.validate()

    def test_validate_page_type_pattern_mismatch(self):
        # page_type not matching pattern
        with self.assertRaises(ValueError):
            self.website.page_type = "e"
            self.website.validate()

    def test_validate_page_type_pattern_match(self):
        # page_type matching pattern
        self.website.page_type = "W"
        self.website.validate()

    def test_validate_invalid_scraped_from_type(self):
        # scraped_from invalid type
        with self.assertRaises(TypeError):
            self.website.scraped_from = None
            self.website.validate()

    def test_validate_scraped_from_too_long(self):
        # scraped_from too long (255)
        with self.assertRaises(ValueError):
            self.website.scraped_from = self.too_long_string
            self.website.validate()

    def test_validate_no_screenshots(self):
        # no screenshots
        with self.assertRaises(ValueError):
            copy = self.website.screenshots.copy()
            self.website.screenshots = []
            self.website.validate()

    def test_validate_no_labels(self):
        # no labels
        with self.assertRaises(ValueError):
            self.website.labels = []
            self.website.validate()

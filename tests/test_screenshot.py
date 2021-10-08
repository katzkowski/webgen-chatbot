import unittest

from src.schemas.screenshot import Screenshot


class TestScreenshot(unittest.TestCase):
    def setUp(self):
        # 256 characters long
        self.too_long_string = "C7Thkl2AQpWemHiAPbEpeXr96r37X0PItQcs5qxiSx3zWT0dMJ5gA3NUvHjszCAXUUCinuVDGAcVDaX6INKyojuyxObhHudXGKBVD1a3A0MpjnINGt2pbPw0NqGqBPTUxIfrxfSeInkKIT4GimLC8IgtEjYgFGhaBuTbN3Fzj73yZ3FrcJVgyTeDRlgL2zMpOKed0YSMDQbLwLJ8lcLWc1SDGUImNpgsRpxf844M5fJmQg1exrH2gfd36qwb1OY3"
        # valid screenshot
        self.screenshot = Screenshot(
            "https://www.awwwards.com/sites/martin-laxenaire-21-portfolio",
            "https://assets.awwwards.com/awards/sites_of_the_day/2021/04/martin-laxenaire-1.jpg",
            None,
            None,
            None,
            None,
        )

    def test_validate_valid_screenshot(self):
        # valid screenshot throws no exception
        self.screenshot.validate()

    def test_validate_invalid_img_url_type(self):
        with self.assertRaises(TypeError):
            self.screenshot.img_url = None
            self.screenshot.validate()

    def test_validate_img_url_too_long(self):
        with self.assertRaises(ValueError):
            self.screenshot.img_url = self.too_long_string
            self.screenshot.validate()

    def test_validate_img_url_pattern_mismatch(self):
        with self.assertRaises(ValueError):
            self.screenshot.img_url = (
                "https://www.awwwards.com/sites/martin-laxenaire-21-portfolio"
            )
            self.screenshot.validate()

    def test_validate_invalid_page_url_type(self):
        with self.assertRaises(TypeError):
            self.screenshot.page_url = None
            self.screenshot.validate()

    def test_validate_page_url_too_long(self):
        with self.assertRaises(ValueError):
            self.screenshot.page_url = self.too_long_string
            self.screenshot.validate()

    def test_validate_page_url_pattern_mismatch(self):
        with self.assertRaises(ValueError):
            self.screenshot.page_url = "https://assets.awwwards.com/awards/sites_of_the_day/2021/04/martin-laxenaire-1.jpg"
            self.screenshot.validate()

    def test_validate_invalid_img_path_type(self):
        # integer as img_path
        with self.assertRaises(TypeError):
            self.screenshot.img_path = 123
            self.screenshot.validate()

        # None as img_path is allowed
        self.screenshot.img_path = None
        self.screenshot.validate()

    def test_validate_img_path_too_long(self):
        with self.assertRaises(ValueError):
            self.screenshot.img_path = self.too_long_string
            self.screenshot.validate()

    def test_validate_invalid_img_size_type(self):
        # string as img_size
        with self.assertRaises(TypeError):
            self.screenshot.img_size = "not allowed"
            self.screenshot.validate()

        # None as img_size is allowed
        self.screenshot.img_size = None
        self.screenshot.validate()

    def test_validate_invalid_dimension_x_type(self):
        # string as dimension_x
        with self.assertRaises(TypeError):
            self.screenshot.dimension_x = "not allowed"
            self.screenshot.validate()

        # None as dimension_x is allowed
        self.screenshot.dimension_x = None
        self.screenshot.validate()

    def test_validate_invalid_dimension_y_type(self):
        # string as dimension_y
        with self.assertRaises(TypeError):
            self.screenshot.dimension_y = "not allowed"
            self.screenshot.validate()

        # None as dimension_y is allowed
        self.screenshot.dimension_y = None
        self.screenshot.validate()

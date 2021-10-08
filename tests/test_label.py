import unittest

from src.schemas.label import Label


class TestLabel(unittest.TestCase):
    def setUp(self):
        # 256 characters long
        self.too_long_string = "C7Thkl2AQpWemHiAPbEpeXr96r37X0PItQcs5qxiSx3zWT0dMJ5gA3NUvHjszCAXUUCinuVDGAcVDaX6INKyojuyxObhHudXGKBVD1a3A0MpjnINGt2pbPw0NqGqBPTUxIfrxfSeInkKIT4GimLC8IgtEjYgFGhaBuTbN3Fzj73yZ3FrcJVgyTeDRlgL2zMpOKed0YSMDQbLwLJ8lcLWc1SDGUImNpgsRpxf844M5fJmQg1exrH2gfd36qwb1OY3"
        self.label = Label("Art & Illustration", "category", "art-illustration")

    def test_validate_valid_label(self):
        # valid label throws no exception
        self.label.validate()

    def test_validate_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.label.name = None
            self.label.validate()

        with self.assertRaises(TypeError):
            self.label.name = 23
            self.label.validate()

    def test_validate_name_too_long(self):
        with self.assertRaises(ValueError):
            self.label.name = self.too_long_string
            self.label.validate()

    def test_validate_invalid_labeltype_type(self):
        with self.assertRaises(TypeError):
            self.label.label_type = None
            self.label.validate()

        with self.assertRaises(TypeError):
            self.label.label_type = 23
            self.label.validate()

    def test_validate_labeltype_too_long(self):
        with self.assertRaises(ValueError):
            self.label.label_type = self.too_long_string
            self.label.validate()

    def test_validate_invalid_href_type(self):
        with self.assertRaises(TypeError):
            self.label.href = None
            self.label.validate()

        with self.assertRaises(TypeError):
            self.label.href = 23
            self.label.validate()

    def test_validate_href_too_long(self):
        with self.assertRaises(ValueError):
            self.label.name = self.too_long_string
            self.label.validate()

    def test_validate_href_pattern_mismatch(self):
        with self.assertRaises(ValueError):
            self.label.href = "Germany"
            self.label.validate()

        with self.assertRaises(ValueError):
            self.label.href = "-Invalid"
            self.label.validate()

        with self.assertRaises(ValueError):
            self.label.href = "invalid space"
            self.label.validate()

        # type == country raises no error
        self.label.href = "Germany"
        self.label.label_type = "country"
        self.label.validate()

        self.label.href = "United Kingdom"
        self.label.validate()

        self.label.href = "Hong Kong - Macau"
        self.label.validate()

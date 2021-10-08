import unittest

from mysql.connector import DatabaseError, Error
from src.database import db_connector as db_con
from src.database.db_setup import TABLES
from src.schemas.label import Label
from src.schemas.screenshot import Screenshot
from src.schemas.website import Website


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.cnx = db_con.connect_to_mysql_server()
        self.cursor = db_con.get_connection_cursor(self.cnx)
        self.db_name = "test_database"
        self.label = Label("Food & Drink", "category", "food-drink")

        # testing screenshot
        self.screenshot = Screenshot(
            "https://www.awwwards.com/sites/proxy",
            "https://assets.awwwards.com/awards/submissions/2021/04/608823823fff0615519193.png",
            None,
            None,
            918,
            656,
        )

        # testing website
        self.website = Website(
            "Proxy",
            "https://www.awwwards.com/sites/proxy",
            "n",
            "awwwards",
            [self.screenshot],
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

    def test_create_database(self):
        # None as db_name
        with self.assertRaises(AttributeError):
            db_con.create_database(None, self.cnx)

        # empty string as db_name
        with self.assertRaises(AttributeError):
            db_con.create_database("", self.cnx)

        # None as cnx
        with self.assertRaises(AttributeError):
            db_con.create_database(self.db_name, None)

        # create database
        db_con.create_database(self.db_name, self.cnx)

        # create duplicate database
        with self.assertRaises(DatabaseError):
            db_con.create_database(self.db_name, self.cnx)

    def test_use_database(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # None as db_name
        with self.assertRaises(AttributeError):
            db_con.use_database(None, self.cursor)

        # empty string as db_name
        with self.assertRaises(AttributeError):
            db_con.use_database("", self.cursor)

        # not existing database as db_name
        with self.assertRaises(DatabaseError):
            db_con.use_database("invalid", self.cursor)

        # None as cursor
        with self.assertRaises(AttributeError):
            db_con.use_database(self.db_name, None)

        # valid arguments
        db_con.use_database(self.db_name, self.cursor)

    def test_create_table(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        table_query = TABLES["websites"]

        # create table
        db_con.create_table(self.db_name, table_query, self.cursor)

        # already existing table raises no exception
        db_con.create_table(self.db_name, table_query, self.cursor)

    def test_insert_website(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        table_query = TABLES["websites"]
        # create table
        db_con.create_table(self.db_name, TABLES["websites"], self.cursor)

        # insert website
        db_con.insert_website(self.db_name, self.website, self.cursor)

        try:
            query = """
                SELECT * FROM websites WHERE url=%s;
                """
            self.cursor.execute(query, (self.website.url,))
        except Error as err:
            print(err)
        # only one result
        self.assertTrue(len(self.cursor.fetchall()) == 1)

    def test_insert_screenshot(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create websites table
        db_con.create_table(self.db_name, TABLES["websites"], self.cursor)

        # insert website
        db_con.insert_website(self.db_name, self.website, self.cursor)

        # create screenshots table
        db_con.create_table(self.db_name, TABLES["screenshots"], self.cursor)

        # insert screenshot
        db_con.insert_screenshot(self.db_name, self.screenshot, self.cursor)

        try:
            query = """
                SELECT * FROM screenshots WHERE image_url=%s;
                """
            self.cursor.execute(query, (self.screenshot.img_url,))
        except Error as err:
            print(err)

        # only one result
        results = self.cursor.fetchall()
        self.assertTrue(len(results) == 1)

        # result matches with input screenshot
        self.assertTrue(results[0][1] == self.screenshot.page_url)
        self.assertTrue(results[0][2] == self.screenshot.img_url)
        self.assertTrue(results[0][3] == self.screenshot.img_path)
        self.assertTrue(results[0][4] == self.screenshot.img_size)
        self.assertTrue(results[0][5] == self.screenshot.dimension_x)
        self.assertTrue(results[0][6] == self.screenshot.dimension_y)

    def test_insert_label(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create table
        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)

        # insert valid label
        db_con.insert_label(self.db_name, self.label, self.cursor)

        # check if valid label was inserted
        try:
            self.cursor.execute(
                """
                SELECT * FROM labels WHERE name='Food & Drink';
                """
            )
        except Error as err:
            print(err)

        # only one result
        results = self.cursor.fetchall()
        self.assertTrue(len(results) == 1)

        # result matches with input label
        self.assertTrue(results[0][1] == self.label.name)
        self.assertTrue(results[0][2] == self.label.label_type)
        self.assertTrue(results[0][3] == self.label.href)

    def test_insert_website_label(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create tables
        table_query = TABLES["websites"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test website
        db_con.insert_website(self.db_name, self.website, self.cursor)

        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test label
        db_con.insert_label(self.db_name, self.label, self.cursor)

        table_query = TABLES["website_labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)

        # string as website_id
        with self.assertRaises(TypeError):
            db_con.insert_website_label(self.db_name, "no", 1, self.cursor)

        # None as website_id
        with self.assertRaises(TypeError):
            db_con.insert_website_label(self.db_name, None, 1, self.cursor)

        # string as label_id
        with self.assertRaises(TypeError):
            db_con.insert_website_label(self.db_name, 1, "no", self.cursor)

        # None as label_id
        with self.assertRaises(TypeError):
            db_con.insert_website_label(self.db_name, 1, None, self.cursor)

        # valid mapping
        db_con.insert_website_label(self.db_name, 1, 1, self.cursor)

        # check if valid website_label was inserted
        try:
            self.cursor.execute(
                """
                SELECT * FROM website_labels WHERE website_id='1';
                """
            )
        except Error as err:
            print(err)

        # only one result
        results = self.cursor.fetchall()
        self.assertTrue(len(results) == 1)

        # result matches with input website_label
        self.assertTrue(results[0][0] == 1)
        self.assertTrue(results[0][1] == 1)

    def test_delete_website_data(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create tables
        table_query = TABLES["websites"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test website
        db_con.insert_website(self.db_name, self.website, self.cursor)

        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test label
        db_con.insert_label(self.db_name, self.label, self.cursor)

        table_query = TABLES["website_labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)

        # create screenshots table
        db_con.create_table(self.db_name, TABLES["screenshots"], self.cursor)

        # insert screenshot
        db_con.insert_screenshot(self.db_name, self.screenshot, self.cursor)

        # string as website_id
        with self.assertRaises(TypeError):
            db_con.delete_website_data(self.db_name, "no", self.cursor)

        # None as website_id
        with self.assertRaises(TypeError):
            db_con.delete_website_data(self.db_name, None, self.cursor)

        # valid delete
        db_con.delete_website_data(self.db_name, 1, self.cursor)

        # check if website was deleted from websites table
        try:
            self.cursor.execute(
                """
                SELECT * FROM websites WHERE id='1';
                """
            )
        except Error as err:
            print(err)

        # no results
        websites = self.cursor.fetchall()
        self.assertTrue(len(websites) == 0)

        # check if website was deleted from screenshots table
        try:
            self.cursor.execute(
                """
                SELECT * FROM screenshots WHERE page_url=%s;
                """,
                (self.website.url,),
            )
        except Error as err:
            print(err)

        # no results
        screenshots = self.cursor.fetchall()
        self.assertTrue(len(screenshots) == 0)

        # website was deleted from website_lables table
        try:
            self.cursor.execute(
                """
                SELECT * FROM website_labels WHERE website_id='1';
                """
            )
        except Error as err:
            print(err)

        # no results
        website_labels = self.cursor.fetchall()
        self.assertTrue(len(website_labels) == 0)

    def test_get_all_labels(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test label
        db_con.insert_label(self.db_name, self.label, self.cursor)

        result = db_con.get_all_labels(self.db_name, self.cursor)

        self.assertTrue(len(result) == 1)
        self.assertTrue(result == [self.label])

    def test_get_website_by_url(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create tables
        table_query = TABLES["websites"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test website
        db_con.insert_website(self.db_name, self.website, self.cursor)

        # invalid url pattern
        with self.assertRaises(ValueError):
            db_con.get_website_by_url(
                self.db_name,
                "https://www.awwwards.com/websites/architecture/",
                self.cursor,
            )

        # get valid url
        ws = db_con.get_website_by_url(self.db_name, self.website.url, self.cursor)

        # check website id
        self.assertTrue(isinstance(ws[0], int))

        # check website object
        self.assertTrue(ws[1].title == self.website.title)
        self.assertTrue(ws[1].url == self.website.url)
        self.assertTrue(ws[1].page_type == self.website.page_type)
        self.assertTrue(ws[1].scraped_from == self.website.scraped_from)

        # get not existent website
        ws = db_con.get_website_by_url(
            self.db_name, "https://www.awwwards.com/sites/not-existent", self.cursor
        )
        self.assertTrue(ws is None)

    def test_get_label_by_name(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create tables
        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test website
        db_con.insert_label(self.db_name, self.label, self.cursor)

        # get valid label
        lb = db_con.get_label_by_name(self.db_name, self.label.name, self.cursor)

        # check label id
        self.assertTrue(isinstance(lb[0], int))

        # check label object
        self.assertTrue(lb[1] == self.label)

        # get not existent label
        lb = db_con.get_label_by_name(self.db_name, "Not existent label", self.cursor)
        self.assertTrue(lb is None)

    def test_get_label_by_href(self):
        # setup: create database
        db_con.create_database(self.db_name, self.cnx)

        # create tables
        table_query = TABLES["labels"]
        db_con.create_table(self.db_name, table_query, self.cursor)
        # insert test website
        db_con.insert_label(self.db_name, self.label, self.cursor)

        # get valid label
        lb = db_con.get_label_by_href(self.db_name, self.label.href, self.cursor)

        # check label id
        self.assertTrue(isinstance(lb[0], int))

        # check label object
        self.assertTrue(lb[1] == self.label)

        # get not existent label
        lb = db_con.get_label_by_href(self.db_name, "not-existent-href", self.cursor)
        self.assertTrue(lb is None)

    def tearDown(self):
        # drop test database and close connection
        try:
            self.cursor.execute(f"DROP DATABASE {self.db_name}")
            self.cursor.close()
            self.cnx.close()
        except Error as err:
            print(err)


if __name__ == "__main__":
    unittest.main()

import logging
import os
import re
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from mysql.connector import (
    DatabaseError,
    Error,
    MySQLConnection,
    connect,
    cursor,
    errorcode,
)
from mysql.connector.cursor import MySQLCursor
from src.schemas.label import Label
from src.schemas.screenshot import Screenshot
from src.schemas.website import Website, website_url_pattern

load_dotenv()

log = logging.getLogger("db")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def connect_to_mysql_server() -> MySQLConnection:
    """Connects to the MySQL Server without specifiying a database.

    Raises:
        connection_error: error occured during connection

    Returns:
        OMySQLConnection: MySQLConnection object
    """
    try:
        return connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)
    except Error as connection_error:
        log.error(connection_error)
        raise connection_error


def connect_to_database(db_name: str) -> MySQLConnection:
    """Connects to a specific database of the MySQL Server.

    Args:
        db_name (str): database to connect with

    Raises:
        connection_error: error occured during connection

    Returns:
        MySQLConnection: MySQLConnection object
    """
    try:
        return connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name,
        )
    except Error as connection_error:
        log.error(connection_error)
        raise connection_error


def get_connection_cursor(cnx: MySQLConnection) -> MySQLCursor:
    """Returns the conncection cursor of the specified connection.

    Args:
        cnx (MySQLConnection): connection to get a cursor for

    Raises:
        Error: cursor retrieval failed

    Returns:
        MySQLCursor: cursor for the connection
    """
    try:
        return cnx.cursor()
    except Error as err:
        raise Error(f"Connection cursor error: {err}")


def create_database(db_name: str, cnx: MySQLConnection) -> None:
    """Creates a new database with name `db_name`.

    Args:
        db_name (str): name of the new database
        cnx (MySQLConnection): connection to the MySQL Server

    Raises:
        AttributeError: invalid or empty database name
                        cnx is None
        DatabaseError: error during cursor retrievial
                       database already exists
                       an error occured during creation
    """
    if db_name == None or not db_name:
        raise AttributeError(
            "Database creation failed: db_name is either None or empty."
        )

    if cnx == None:
        raise AttributeError("Database creation failed: connection is None.")

    # get cursor
    try:
        cursor = get_connection_cursor(cnx)
    except Error:
        raise DatabaseError("Database creation failed: error while retrieving cursor.")

    # check if database exists
    try:
        cursor.execute(f"USE {db_name}")
    except Error:
        log.info(f"Database {db_name} does not yet exist. Creating database...")
    else:
        raise DatabaseError(
            f"Database creation failed: database {db_name} already exists."
        )

    # create new database
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
    except Error as err:
        raise DatabaseError(f"Database creation failed: {err}")
    else:
        cnx.database = db_name
        log.info(f"Database {db_name} created successfully")


def use_database(db_name: str, cursor: MySQLCursor) -> None:
    """Use the specified database.

    Args:
        db_name (str): the database
        cursor (MySQLCursor): cursor to server

    Raises:
        AttributeError: db_name is either None or empty
                        invalid cursor type
        DatabaseError: database db_name does not exist
    """
    if db_name == None or not db_name:
        raise AttributeError(
            f"Using database {db_name} failed: db_name is either None or empty."
        )

    if not isinstance(cursor, MySQLCursor):
        raise AttributeError(f"Using database {db_name} failed: invalid cursor type.")

    # use database
    try:
        cursor.execute(f"USE {db_name}")
    except Error:
        raise DatabaseError(
            f"Using database {db_name} failed: database {db_name} does not exist."
        )


def create_table(db_name: str, table_query: str, cursor: MySQLCursor) -> None:
    """Creates a table specified by `table_query` in the database `db_name`.

    Args:
        db_name (str): database to create the table in
        table_query (str): MySQL query specifying the table
        cursor (MySQLCursor): cursor to server

    Raises:
        AttributeError: db_name is either None or empty
                        cursor is not an instance of MySQLCursor
        DatabaseError: database db_name does not exist
        err: sql execution error in table_query
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Table creation failed: {err}")
    except Error as err:
        raise DatabaseError(f"Table creation failed: {err.msg}")

    # execute table query
    try:
        cursor.execute(table_query)
    except Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            log.warning(f"Table already exists in database {db_name}.")
            return
        else:
            log.error(f"Table creation failed: {err}")
            raise err
    else:
        log.info("Table created.")


def insert_website(db_name: str, website: Website, cursor: MySQLCursor):
    """Insert a new website into the websites table of the specified database.

    Args:
        db_name (str): the database
        website (Website): the website
        cursor (MySQLCursor): cursor to server

    Raises:
        TypeError:  raised by website.validate()
        ValueError: raised by website.validate()
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error:  raised by website.validate()
                sql execution error in 'INSERT INTO websites'
    """
    try:
        website.validate()
    except TypeError as err:
        raise TypeError(f"Inserting website {website.title} failed: {err}")
    except ValueError as err:
        raise ValueError(f"Inserting website {website.title} failed: {err}")
    except Error as err:
        raise err

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Inserting website {website.title} failed: {err}")
    except Error as err:
        raise DatabaseError(f"Inserting website {website.title} failed: {err.msg}")

    # insert website into websites table
    try:
        query = """
            INSERT INTO websites (title, url, page_type, scraped_from)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(
            query, (website.title, website.url, website.page_type, website.scraped_from)
        )
    except Error as err:
        log.error(f"Inserting website {website.title} failed: {err}")
        raise err
    else:
        log.info(f"Website {website.title} inserted successfully")


def insert_screenshot(db_name: str, screenshot: Screenshot, cursor: MySQLCursor):
    """Inserts a new screenshot into the screenshot table of the specified database.

    Args:
        db_name (str): the database
        screenshot (Screenshot): the screenshot
        cursor (MySQLCursor): cursor to server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO screenshots'
    """
    # validate screenshot
    try:
        screenshot.validate()
    except TypeError as err:
        raise TypeError(
            f"Inserting screenshot with url {screenshot.img_url} failed: {err}"
        )
    except ValueError as err:
        raise ValueError(
            f"Inserting screenshot with url {screenshot.img_url} failed: {err}"
        )
    except Error as err:
        raise err

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Inserting screenshot with url {screenshot.img_url} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Inserting screenshot with url {screenshot.img_url} failed: {err}"
        )

    # insert screenshot into screenshots table
    try:
        query = """
            INSERT INTO screenshots (page_url, image_url, image_path,    image_size, dimension_x, dimension_y)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            query,
            (
                screenshot.page_url,
                screenshot.img_url,
                screenshot.img_path,
                screenshot.img_size,
                screenshot.dimension_x,
                screenshot.dimension_y,
            ),
        )
    except Error as err:
        log.warning(
            "MySQL could be running in strict mode, which prevents assigning NULL values to INT columns."
        )
        log.error(f"Inserting screenshot with url {screenshot.img_url} failed: {err}")
        raise err
    else:
        log.info(f"Screenshot with url {screenshot.img_url} inserted successfully")


def delete_screenshot(db_name: str, screenshot_id: int, cursor: MySQLCursor) -> None:
    """Deletes the screenshot with `screenshot_id` from the specified database.

    Args:
        db_name (str): the database
        screenshot_id (int): id of the screenshot to be deleted
        cursor (MySQLCursor): cursor of the database

    Raises:
        AttributeError: raised by use_database()
                        screenshot_id is None or not instance of int
        DatabaseError: raised by use_database()
        Error: sql execution error in 'DELETE FROM screenshots'
    """
    if screenshot_id is None or not isinstance(screenshot_id, int):
        raise AttributeError(
            f"Deleting screenshot with id {screenshot_id} failed: screenshot_id is None or not an instance of int"
        )

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Deleting screenshot with id {screenshot_id} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Deleting screenshot with id {screenshot_id} failed: {err}"
        )

    # delete screenshot from table screenshots
    try:
        query = """
            DELETE FROM screenshots WHERE id=%s;
        """
        cursor.execute(query, (screenshot_id,))
    except Error as err:
        log.error(f"Deleting screenshot with id {screenshot_id} failed: {err}")
        raise err
    else:
        log.info(f"Deleted screenshot with id {screenshot_id} successfully")


def insert_label(db_name: str, label: Label, cursor: MySQLCursor):
    """Inserts a new label into the labels table of the specified database.

    Args:
        db_name (str): the database
        label (Label): the label
        cursor (MySQLCursor): cursor to server

    Raises:
        TypeError:  raised by label.validate()
        ValueError: raised by label.validate()
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO labels'
               raised by label.validate()
    """
    try:
        label.validate()
    except TypeError as err:
        raise TypeError(f"Inserting label {label.name} failed: {err}")
    except ValueError as err:
        raise ValueError(f"Inserting label {label.name} failed: {err}")
    except Error as err:
        raise err

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Inserting label {label.name} failed: {err}")
    except Error as err:
        raise DatabaseError(f"Inserting label {label.name} failed: {err}")

    # insert label
    try:
        query = """
            INSERT INTO labels (name, type, href)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (label.name, label.label_type, label.href))
    except Error as err:
        log.error(f"Inserting label {label} failed: {err}")
        raise err
    else:
        log.info(f"Inserted label {label} successfully")


def insert_website_label(
    db_name: str, website_id: int, label_id: int, cursor: MySQLCursor
):
    """Inserts a website-label mapping into the specified database.

    Args:
        website_id (int): website id
        label_id (int): label id
        cursor (MySQLCursor): cursor to server

    Raises:
        TypeError:  website_id is None or not an instance of int
                    label_id is None or not an instance of int
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO website_labels'
    """
    if website_id is None or not isinstance(website_id, int):
        raise TypeError(
            f"Inserting website_label failed: website_id {website_id} is None or not an instance of int."
        )

    if label_id is None or not isinstance(label_id, int):
        raise TypeError(
            f"Inserting website_label failed: label_id {label_id} is None or not an instance of int."
        )

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Inserting website_label failed: {err}")
    except Error as err:
        raise DatabaseError(f"Inserting website_label failed: {err}")

    # insert website_label
    try:
        query = """
            INSERT INTO website_labels (website_id, label_id)
            VALUES (%s, %s);
        """
        cursor.execute(query, (website_id, label_id))
    except Error as err:
        log.error(f"Inserting website_label failed: failed: {err}")
        raise err
    else:
        log.info(f"Inserted website_label successfully")


def delete_website_data(db_name: str, website_id: int, cursor: MySQLCursor):
    """Delete a website with all screenshots and label assignments in the specified database.

    Args:
        db_name (str): the database
        website_id (int): the website id
        cursor (MySQLCursor): cursor to server

    Raises:
        TypeError: website_id is None or not an instance of int
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'DELETE FROM websites'
    """

    if website_id is None or not isinstance(website_id, int):
        raise TypeError(
            f"Deleting website data failed: website_id {website_id} is None or not an instance of int."
        )

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Deleting website data failed: {err}")
    except Error as err:
        raise DatabaseError(f"Deleting website data failed: {err}")

    # delete website from tables: websites, screenshots, website_labels
    try:
        query = """
            DELETE FROM websites WHERE id=%s;
        """
        cursor.execute(query, (website_id,))
    except Error as err:
        log.error(f"Deleting website data failed: {err}")
        raise err
    else:
        log.info(f"Deleted website data successfully")


def get_all_labels(db_name: str, cursor: MySQLCursor) -> List[Label]:
    """Returns all labels stored in the specified database.

    Args:
        db_name (str): the database
        cursor (MySQLCursor): cursor to server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'SELECT * FROM labels'

    Returns:
        List[Label]: [description]
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Retrieving all labels failed: {err}")
    except Error as err:
        raise DatabaseError(f"Retrieving all labels failed: {err}")

    try:
        query = """
            SELECT * FROM labels;
        """
        cursor.execute(query)

        results = list(
            map(
                lambda result: Label(result[1], result[2], result[3]), cursor.fetchall()
            )
        )
    except Error as err:
        log.error(f"Retrieving all labels failed: {err}")
        raise err
    else:
        return results


def get_website_by_url(
    db_name: str, url: str, cursor: MySQLCursor
) -> Optional[Tuple[int, Website]]:
    """Searches the database for a specific url and returns the id and the Website object (without screenshots, labels and html), or None if not existent.

    Args:
        db_name (str): the database
        url (str): the url of the website
        cursor (MySQLCursor): cursor of the server

    Raises:
        ValueError: url does not match url pattern
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'SELECT * FROM websites'

    Returns:
        Optional[Tuple[int, Website]]: website id and object
    """

    # validate url format
    if not website_url_pattern.match(url):
        raise ValueError("get_website_by_url failed: website url pattern mismatch")

    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"get_website_by_url failed: {err}")
    except Error as err:
        raise DatabaseError(f"get_website_by_url failed: {err}")

    try:
        query = """
                SELECT * FROM websites WHERE url=%s;
                """
        cursor.execute(query, (url,))

        result = cursor.fetchone()

        if result is None:
            return None

        website = Website(result[1], result[2], result[3], result[4])
    except Error as err:
        log.error(f"get_website_by_url failed: {err}")
        raise err
    else:
        return (result[0], website)


def get_label_by_name(
    db_name: str, label_name: str, cursor: MySQLCursor
) -> Optional[Tuple[int, Label]]:
    """Searches the database for a specific label name and returns the id and the Label object, or None if not existent.

    Args:
        db_name (str): the database
        label_name (str): the name of the label
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'SELECT * FROM labels'

    Returns:
        Optional[Tuple[int, Label]]: label id and object
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"get_label_by_name failed: {err}")
    except Error as err:
        raise DatabaseError(f"get_label_by_name failed: {err}")

    try:
        query = """
                SELECT * FROM labels WHERE name=%s;
                """
        cursor.execute(query, (label_name,))

        result = cursor.fetchone()

        if result is None:
            return None

        label = Label(result[1], result[2], result[3])
    except Error as err:
        log.error(f"get_label_by_name failed: {err}")
        raise err
    else:
        return (result[0], label)


def get_label_by_href(
    db_name: str, label_href: str, cursor: MySQLCursor
) -> Optional[Tuple[int, Label]]:
    """Searches the database for a specific label href and returns the id and the Label object, or None if not existent.

    Args:
        db_name (str): the database
        label_href(str): the href of the label
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'SELECT * FROM labels'

    Returns:
        Optional[Tuple[int, Label]]: label id and object
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"get_label_by_name failed: {err}")
    except Error as err:
        raise DatabaseError(f"get_label_by_name failed: {err}")

    try:
        query = """
                SELECT * FROM labels WHERE href=%s;
                """
        cursor.execute(query, (label_href,))

        result = cursor.fetchone()

        if result is None:
            return None

        id = result[0]
        label = Label(result[1], result[2], result[3])
    except Error as err:
        log.error(f"get_label_by_href failed: {err}")
        raise err
    else:
        return (id, label)


def get_screenshot_by_path(
    db_name: str, image_path: str, cursor: MySQLCursor
) -> Optional[Tuple[int, Screenshot]]:
    """Searches the database for a specific screenshot path and returns the id and the Screenshot object, or None if not existent.
    Args:
        db_name (str): name of the database
        image_path (str): path of the screenshot
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'SELECT * FROM screenshots'

    Returns:
        Optional[Tuple[int, Screenshot]]: screenshot id and object
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(f"Getting screenshot for path {image_path} failed: {err}")
    except Error as err:
        raise DatabaseError(f"Getting screenshot for path {image_path} failed: {err}")

    try:
        query = """
                SELECT * FROM screenshots WHERE image_path=%s;
                """
        cursor.execute(query, (image_path,))

        result = cursor.fetchone()

        if result is None:
            return None

        id = result[0]
        scr = Screenshot(
            result[1], result[2], result[3], result[4], result[5], result[6]
        )
    except Error as err:
        log.error(f"Getting screenshot for path {image_path} failed: {err}")
        raise err
    else:
        return (result[0], scr)


def insert_clustering_run(
    db_name: str,
    run_name: str,
    k_value: int,
    n_screenshots: int,
    n_components: int,
    cursor: MySQLCursor,
) -> None:
    """Inserts a new clustering run into the specified database.

    Args:
        db_name (str): name of the database
        run_name (str): name of the clustering run
        k_value (int): k-value of clustering run
        n_screenshots (int): number of screenshots
        n_components (int): number of PCA components
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO clustering_runs'
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Inserting clustering_run {run_name} with k={k_value} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Inserting clustering_run {run_name} with k={k_value} failed: {err}"
        )

    # insert clustering run
    try:
        query = """
            INSERT INTO clustering_runs (name, k_value, n_screenshots, n_components)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (run_name, k_value, n_screenshots, n_components))
    except Error as err:
        log.error(f"Inserting clustering_run {run_name} with k={k_value} failed: {err}")
        raise err
    else:
        log.info(f"Inserted clustering_run {run_name} with k={k_value} successfully")


def insert_cluster(
    db_name: str,
    cluster_id: str,
    run_name: str,
    k_value: int,
    n_screenshots: int,
    cursor: MySQLCursor,
) -> None:
    """Inserts a new cluster into the specified database.

    Args:
        db_name (str): name of the database
        cluster_id (str): id of the cluster
        run_name (str): name of clustering run
        k_value (int): k-value of clustering run
        n_screenshots (int): number of screenshots in cluster
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO clusters'
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Inserting cluster {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Inserting cluster {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )

    # insert cluster
    try:
        query = """
            INSERT INTO clusters (cluster_id, run_name, k_value, n_screenshots)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (cluster_id, run_name, k_value, n_screenshots))
    except Error as err:
        log.error(
            f"Inserting cluster {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )
        raise err
    else:
        log.info(
            f"Inserted cluster {cluster_id} with k={k_value} for run {run_name} successfully"
        )


def insert_cluster_assignment(
    db_name: str,
    cluster_id: str,
    run_name: str,
    k_value: int,
    screenshot_id: int,
    cursor: MySQLCursor,
) -> None:
    """Inserts a cluster assignment for a screenshot into the specified database.

    Args:
        db_name (str): name of the database
        cluster_id (str): id of the cluster
        run_name (str): name of clustering run
        k_value (int): k-value of clustering run
        screenshot_id (int): id of the screenshot
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO cluster_screenshots'
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Inserting cluster assignment for screenshot with id {screenshot_id} to {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Inserting cluster assignment for screenshot with id {screenshot_id} to {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )

    # insert cluster-screenshots mapping
    try:
        query = """
            INSERT INTO cluster_screenshots (cluster_id, run_name, k_value, screenshot_id)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (cluster_id, run_name, k_value, screenshot_id))
    except Error as err:
        log.error(
            f"Inserting cluster assignment for screenshot with id {screenshot_id} to {cluster_id} with k={k_value} for run {run_name} failed: {err}"
        )
        raise err
    else:
        log.info(
            f"Inserted cluster assignment for screenshot with id {screenshot_id} to {cluster_id} with k={k_value} for run {run_name} successfully"
        )


def insert_cluster_matching(
    db_name: str,
    cluster_id: str,
    run_name: str,
    k_value: int,
    label_name: str,
    label_count: int,
    cursor: MySQLCursor,
) -> None:
    """Inserts a cluster-label matching into the specified database.

    Args:
        db_name (str): name of the database
        cluster_id (str): id of the cluster
        run_name (str): name of clustering run
        k_value (int): k-value of clustering run
        label_name (str): name of the label
        label_count (int): amount of screenshots with label
        cursor (MySQLCursor): cursor of the server

    Raises:
        AttributeError: raised by use_database()
        DatabaseError: raised by use_database()
        Error: sql execution error in 'INSERT INTO matchings'
    """
    # use database
    try:
        use_database(db_name, cursor)
    except AttributeError as err:
        raise AttributeError(
            f"Inserting cluster matching for cluster with id {cluster_id} to {label_name} with k={k_value} for run {run_name} failed: {err}"
        )
    except Error as err:
        raise DatabaseError(
            f"Inserting cluster matching for cluster with id {cluster_id} to {label_name} with k={k_value} for run {run_name} failed: {err}"
        )

    # insert cluster-label matching
    try:
        query = """
            INSERT INTO matchings (cluster_id, run_name, k_value, label_name, cluster_label_count)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (cluster_id, run_name, k_value, label_name, label_count))
    except Error as err:
        log.error(
            f"Inserting cluster matching for cluster with id {cluster_id} to {label_name} with k={k_value} for run {run_name} failed: {err}"
        )
        raise err
    else:
        log.info(
            f"Inserted cluster matching for cluster with id {cluster_id} to {label_name} with k={k_value} for run {run_name} successfully"
        )

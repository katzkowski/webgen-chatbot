DATABASES = {}

# schemas for crawling_db
crawling_schema = {}
crawling_schema[
    "websites"
] = """CREATE TABLE websites 
    (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    url VARCHAR(255) NOT NULL UNIQUE,
    page_type CHAR(1),
    scraped_from VARCHAR(255),
    PRIMARY KEY (id),
    INDEX (url)
    );
    """
crawling_schema[
    "screenshots"
] = """CREATE TABLE screenshots
    (
        id INT NOT NULL AUTO_INCREMENT,
        page_url VARCHAR(255) NOT NULL,
        image_url VARCHAR(255) NOT NULL UNIQUE,
        image_path VARCHAR(255),
        image_size INT,
        dimension_x SMALLINT,
        dimension_y SMALLINT,
        PRIMARY KEY (id),
        FOREIGN KEY(page_url) REFERENCES websites(url) ON DELETE CASCADE,
        INDEX (image_url)
    );
    """
crawling_schema[
    "labels"
] = """CREATE TABLE labels
    (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL UNIQUE,
        type VARCHAR(255),
        href VARCHAR(255) UNIQUE,
        PRIMARY KEY (id)
    );
    """
crawling_schema[
    "website_labels"
] = """CREATE TABLE website_labels
    (
        website_id INT NOT NULL,
        label_id INT NOT NULL,
        PRIMARY KEY (website_id, label_id),
        FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE CASCADE,
        FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE
    );
    """

# schemas for clustering_db
clustering_schema = {}
clustering_schema[
    "websites"
] = """CREATE TABLE websites 
    (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    url VARCHAR(255) NOT NULL UNIQUE,
    page_type CHAR(1),
    scraped_from VARCHAR(255),
    PRIMARY KEY (id),
    INDEX (url)
    );
    """
clustering_schema[
    "screenshots"
] = """CREATE TABLE screenshots
    (
        id INT NOT NULL AUTO_INCREMENT,
        page_url VARCHAR(255) NOT NULL,
        image_url VARCHAR(255) NOT NULL UNIQUE,
        image_path VARCHAR(255),
        image_size INT,
        dimension_x SMALLINT,
        dimension_y SMALLINT,
        PRIMARY KEY (id),
        FOREIGN KEY(page_url) REFERENCES websites(url) ON DELETE CASCADE,
        INDEX (image_url)
    );
    """
clustering_schema[
    "labels"
] = """CREATE TABLE labels
    (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL UNIQUE,
        type VARCHAR(255),
        href VARCHAR(255) UNIQUE,
        count INT,
        PRIMARY KEY (id)
    );
    """
clustering_schema[
    "website_labels"
] = """CREATE TABLE website_labels
    (
        website_id INT NOT NULL,
        label_id INT NOT NULL,
        PRIMARY KEY (website_id, label_id),
        FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE CASCADE,
        FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE
    );
    """
clustering_schema[
    "clustering_runs"
] = """CREATE TABLE clustering_runs
    (
        name VARCHAR(255) NOT NULL,
        k_value INT NOT NULL,
        n_screenshots INT NOT NULL,
        n_components INT NOT NULL,
        PRIMARY KEY (name, k_value)
    );
    """
clustering_schema[
    "clusters"
] = """CREATE TABLE clusters
    (
        cluster_id INT NOT NULL,
        run_name VARCHAR(255) NOT NULL,
        k_value INT NOT NULL,
        n_screenshots INT NOT NULL,
        PRIMARY KEY (cluster_id, run_name, k_value),
        FOREIGN KEY (run_name, k_value) REFERENCES clustering_runs(name, k_value) ON DELETE CASCADE
    );
    """
clustering_schema[
    "cluster_screenshots"
] = """CREATE TABLE cluster_screenshots
    (
        cluster_id INT NOT NULL,
        run_name VARCHAR(255) NOT NULL,
        k_value INT NOT NULL,
        screenshot_id INT NOT NULL,
        PRIMARY KEY (cluster_id, run_name,k_value, screenshot_id),
        FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id) ON DELETE CASCADE,
        FOREIGN KEY (run_name, k_value) REFERENCES clustering_runs(name, k_value) ON DELETE CASCADE,
        FOREIGN KEY (screenshot_id) REFERENCES screenshots(id) ON DELETE CASCADE
    );
    """
clustering_schema[
    "matchings"
] = """CREATE TABLE matchings
    (
        cluster_id INT NOT NULL,
        run_name VARCHAR(255) NOT NULL,
        k_value INT NOT NULL,
        label_name VARCHAR(255) NOT NULL,
        cluster_label_count INT,
        percentage FLOAT,
        factor FLOAT,
        tf FLOAT,
        idf FLOAT,
        tf_idf FLOAT,
        factor_tf_idf FLOAT,
        PRIMARY KEY (cluster_id, run_name, k_value, label_name),
        FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id) ON DELETE CASCADE,
        FOREIGN KEY (run_name, k_value) REFERENCES clustering_runs(name, k_value) ON DELETE CASCADE,
        FOREIGN KEY (label_name) REFERENCES labels(name) ON DELETE CASCADE
    );
    """


# add databases
DATABASES["crawling_db"] = crawling_schema
DATABASES["clustering_db"] = clustering_schema

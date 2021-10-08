import logging
from typing import List, Tuple

import src.database.db_connector as db

# initalize logging
log = logging.getLogger("training")

# database name for matchings
db_name = "clustering_db"
cnx = None
cursor = None


def run_matcher(args: List[any]) -> None:
    """Run cluster-label matching for all k's of a clustering run.

    Args:
        args (List[any]): command line arguments [run_name]
    """
    target_run = args[0]
    log.info(f"Running matcher for run {target_run}")

    # connect to database
    global cnx, cursor
    cnx = db.connect_to_database(db_name)
    cursor = db.get_connection_cursor(cnx)
    db.use_database(db_name, cursor)

    clustering_runs = get_clustering_runs(target_run)
    log.info(f"Found {str(len(clustering_runs))} k's for {target_run}")

    for name, k_value, _ in clustering_runs:
        # get clusters for run with k
        cluster_list = get_cluster_list(name, k_value)
        log.info(f"Inserting clusters for {name} with k={str(k_value)}")

        for cluster in cluster_list:
            # count labels for each cluster
            log.info(f"Counting labels for cluster {cluster[0]}")
            label_counts = count_labels_for_cluster(name, cluster[0], k_value)

            # insert label-cluster matchings
            log.info(f"Inserting label-cluster matchings for cluster {cluster[0]}")
            for label_name, label_count in label_counts:
                db.insert_cluster_matching(
                    db_name, cluster[0], name, k_value, label_name, label_count, cursor
                )
            cnx.commit()
    log.info(f"Finished label matching for {target_run}")


def get_clustering_runs(name: str) -> List[Tuple[str, int, int]]:
    """Get all clustering runs with a specific name.

    Args:
        name (str): name of the clustering run

    Returns:
        List[Tuple[str, int, int]]: list of [name, k_value, n_screenshots]
    """
    query_clustering_runs = """
        SELECT name, k_value, n_screenshots FROM clustering_runs WHERE name=%s; 
    """
    cursor.execute(query_clustering_runs, (name,))

    return cursor.fetchall()


def get_cluster_list(run_name: str, k_value: int) -> List[Tuple[str, int, int]]:
    """Returns the clusters for `run_name` with `k_value`.

    Args:
        run_name (str): name of the clustering run
        k_value (int): k

    Returns:
        List[Tuple[str, int, int]]: list of [cluster_id, k_value, cluster_size]
    """
    query_cluster_list = """
        SELECT cluster_id, k_value, n_screenshots AS cluster_size FROM clusters WHERE run_name=%s AND k_value=%s; 
    """
    cursor.execute(query_cluster_list, (run_name, k_value))

    return cursor.fetchall()


def count_labels_for_cluster(
    run_name: str, cluster_id: str, cluster_k: int
) -> List[Tuple[str, int]]:
    """Count label occurences for a specific cluster

    Args:
        run_name (str): name of the clustering run
        cluster_id (str): id of the cluster
        cluster_k (int): k value of run

    Returns:
        List[Tuple[str, int]]: list of [label name, label count]
    """
    label_count_query = """
        SELECT l.name, count(*)
        FROM clusters AS c
        INNER JOIN cluster_screenshots AS cs ON c.cluster_id=cs.cluster_id AND c.run_name=cs.run_name AND c.k_value=cs.k_value
        INNER JOIN screenshots AS s ON s.id=cs.screenshot_id
        INNER JOIN websites AS w ON w.url=s.page_url
        INNER JOIN website_labels AS wl ON w.id=wl.website_id
        INNER JOIN labels AS l ON wl.label_id=l.id
        WHERE c.run_name=%s
        AND c.cluster_id=%s
        AND c.k_value=%s
        GROUP BY l.name;
    """
    cursor.execute(label_count_query, (run_name, cluster_id, cluster_k))

    return cursor.fetchall()


def run_evaluation(args: List[any]) -> None:
    """Evaluate cluster-label matching for all k's of a clustering run.

    Args:
        args (List[any]): command line arguments
    """
    target_run = args[0]
    log.info(f"Running evaluation for run {target_run}")

    # connect to database
    global cnx, cursor
    cnx = db.connect_to_database(db_name)
    cursor = db.get_connection_cursor(cnx)
    db.use_database(db_name, cursor)

    # declare factor, tf, idf sql functions
    if not check_sql_metrics():
        log.critical(f"SQL metrics function not set up, exiting program")
        exit(1)

    clustering_runs = get_clustering_runs(target_run)
    log.info(f"Found {str(len(clustering_runs))} k's for {target_run}")

    for name, k_value, run_size in clustering_runs:

        # get clusters for run with k
        for cluster_id in range(0, k_value):
            evaluate_cluster(name, k_value, run_size, cluster_id)

        log.info(f"Evaluated clustering for k={str(k_value)} in run {name}")

    log.info(f"Finished evaluation for run {name}")


def evaluate_cluster(
    run_name: str, k_value: int, run_size: int, cluster_id: int
) -> None:
    """Calculate metrics for a specific cluster and insert them into SQL.

    Args:
        run_name (str): name of the clustering run
        k_value (int): k value
        run_size (int): total number of screenshots
        cluster_id (int): cluster to be evaluated
    """
    # get cluster size
    cluster_size_query = """
        SELECT n_screenshots FROM clusters
        WHERE run_name=%s AND k_value=%s AND cluster_id=%s;
    """
    cursor.execute(cluster_size_query, (run_name, k_value, cluster_id))
    cluster_size = cursor.fetchone()[0]
    log.info(f"Evaluating cluster {str(cluster_id)} with size {str(cluster_size)}")

    # get count of most frequent label within cluster
    max_label_count_query = """
        SELECT MAX(cluster_label_count) FROM matchings
        WHERE run_name=%s AND k_value=%s AND cluster_id=%s;
    """
    cursor.execute(max_label_count_query, (run_name, k_value, cluster_id))
    max_label_count = cursor.fetchone()[0]

    # set up variables separately, because cursor.execute(query, multi=True) does not work
    setup_run_name = "SET @run_name := %s;"
    cursor.execute(setup_run_name, (run_name,))

    setup_k_value = "SET @k_value := %s;"
    cursor.execute(setup_k_value, (k_value,))

    setup_run_size = "SET @run_size := %s;"
    cursor.execute(setup_run_size, (run_size,))

    setup_cluster_id = "SET @cluster_id := %s;"
    cursor.execute(setup_cluster_id, (cluster_id,))

    setup_cluster_size = "SET @cluster_size := %s;"
    cursor.execute(setup_cluster_size, (cluster_size,))

    setup_max_label_count = "SET @max_label_count := %s;"
    cursor.execute(setup_max_label_count, (max_label_count,))

    # calcuate evaluation metrics and update table
    metrics_query = """
        Update matchings as m	
        INNER JOIN labels AS l ON m.label_name=l.name
        SET m.percentage = m.cluster_label_count / @cluster_size, 
            m.factor = factor(m.cluster_label_count, @cluster_size, l.count, @run_size),
            m.tf = tf(m.cluster_label_count, @max_label_count), 
            m.idf = idf(m.cluster_label_count, @cluster_size),
            m.tf_idf = m.tf * m.idf,
            m.factor_tf_idf = m.factor * m.tf * m.idf
        WHERE m.run_name=@run_name AND m.k_value=@k_value AND m.cluster_id=@cluster_id;
    """
    try:
        cursor.execute(metrics_query)
        cnx.commit()
    except Exception as err:
        log.error(
            f"Failed inserting eval. metrics for k={str(k_value)}, cluster {cluster_id}: {err}"
        )
        cnx.rollback()


def check_sql_metrics() -> bool:
    """Check if sql functions for metrics `tf`, `idf` and `factor` exist.

    Returns:
        bool: `True`, if functions are set up, otherwise `False`.
    """
    try:
        # tf fun
        cursor.execute("SELECT tf(1,2);")
        log.info(f"tf(1,2) = {str(cursor.fetchone()[0])}")

        # idf fun
        cursor.execute("SELECT idf(1,2);")
        log.info(f"idf(1,2) = {str(cursor.fetchone()[0])}")

        # factor fun
        cursor.execute("SELECT factor(1,2,1,2);")
        log.info(f"factor(1,2,1,2) = {str(cursor.fetchone()[0])}")

        log.info(f"SQL metric functions are set up: factor, tf, idf")
        return True
    except Exception as err:
        log.error(f"SQL metric functions are NOT set up: {err}")
        return False

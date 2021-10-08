USE clustering_db;

# term frequency 
DROP FUNCTION IF EXISTS tf;
DELIMITER $$
CREATE FUNCTION tf(
	label_count INT, 
    max_label_count INT
) 
RETURNS FLOAT
DETERMINISTIC
BEGIN
	RETURN (label_count / max_label_count);
END$$
DELIMITER ;

# inverse document frequency
DROP FUNCTION IF EXISTS idf;
DELIMITER $$
CREATE FUNCTION idf(
	label_count INT, 
    cluster_size INT
) 
RETURNS FLOAT
DETERMINISTIC
BEGIN
	RETURN log10(cluster_size / label_count);
END$$
DELIMITER ;

# factor
DROP FUNCTION IF EXISTS factor;
DELIMITER $$
CREATE FUNCTION factor(
	label_count INT, 
    cluster_size INT, 
    total_label_count INT,
    run_size INT
) 
RETURNS FLOAT
DETERMINISTIC
BEGIN
	RETURN label_count / (cluster_size * (total_label_count / run_size));
END$$
DELIMITER ;
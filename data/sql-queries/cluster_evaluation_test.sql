SET @run_name := "v01_all_run2_pca90";
SET @run_size := 41222;
SET @k_value := 90;
SET @cluster_id := 4;
SET @cluster_size := NULL;
SET @max_label_count := NULL;

# get cluster size
SELECT n_screenshots FROM clusters
WHERE run_name=@run_name and k_value=@k_value and cluster_id=@cluster_id INTO @cluster_size;

# get count of most frequent label within cluster
SELECT MAX(cluster_label_count) FROM matchings
WHERE run_name=@run_name and k_value=@k_value and cluster_id=@cluster_id INTO @max_label_count;

# calcuate evaluation metrics 
SELECT 
	m.label_name,
	m.cluster_label_count / @cluster_size AS percentage, 
	@factor := factor(m.cluster_label_count, @cluster_size, l.count, @run_size) AS factor,
	@tf := tf(m.cluster_label_count, @max_label_count) AS tf, 
	@idf := idf(m.cluster_label_count, @cluster_size) AS idf,
	@tf * @idf AS tf_idf,
	@factor * @tf * @idf AS factor_tf_idf
FROM matchings AS m
INNER JOIN labels AS l ON m.label_name=l.name
WHERE m.run_name=@run_name AND m.k_value=@k_value AND m.cluster_id=@cluster_id 
order by factor_tf_idf DESC;

# calculate metrics and update table
-- Update matchings as m	
-- INNER JOIN labels AS l ON m.label_name=l.name
-- SET m.percentage = m.cluster_label_count / @cluster_size, 
-- 	m.factor = factor(m.cluster_label_count, @cluster_size, l.count, @run_size),
-- 	m.tf = tf(m.cluster_label_count, @max_label_count), 
-- 	m.idf = idf(m.cluster_label_count, @cluster_size),
-- 	m.tf_idf = m.tf * m.idf,
-- 	m.factor_tf_idf = m.factor * m.tf * m.idf
-- WHERE m.run_name=@run_name AND m.k_value=@k_value AND m.cluster_id=@cluster_id;

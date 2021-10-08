USE clustering_db;

# get top 5 labels for each cluster according to factor_tf_idf
# only outputs data to user
-- DROP PROCEDURE IF EXISTS get_top_labels;
-- DELIMITER //
-- CREATE PROCEDURE get_top_labels(
-- 	run_name VARCHAR(255), 
--     k_value INT,
--     cluster_id INT
-- ) 
-- BEGIN
-- 	SELECT label_name, factor_tf_idf
-- 	FROM matchings AS m
-- 	INNER JOIN labels AS l ON m.label_name=l.name
-- 	WHERE m.run_name=run_name AND m.k_value=k_value AND m.cluster_id=cluster_id
--     ORDER BY factor_tf_idf DESC
--     LIMIT 5;
-- END //

-- DELIMITER ;

-- SET @k_rank := 0;
-- SET @cluster_rank := 0;

-- # rank k's and clusters within k's => top 5 for each cluster for each k 
-- SELECT label_name, count(label_name) FROM (
-- 	SELECT 
-- 	j.cluster_id, 
-- 	j.ranked_k_value, 
-- 	@cluster_rank := if(@current_cluster = j.cluster_id, @cluster_rank  + 1, 1) AS cluster_rank ,
-- 	j.label_name,
--     j.type as label_type,
-- 	j.factor_tf_idf,
-- 	@current_cluster := j.cluster_id
-- 	FROM ( 
-- 		SELECT  *
-- 		FROM matchings AS m
-- 		INNER JOIN ( 
-- 			SELECT ma.k_value as ranked_k_value
-- 			FROM matchings AS ma
-- 			WHERE (ma.run_name = "v01_all_run2_pca90" OR ma.run_name = "v01_all_run3_pca90") 
-- 			group by ma.k_value
-- 		) as ranked_k on ranked_k.ranked_k_value = m.k_value
--         INNER JOIN labels as l on m.label_name = l.name
-- 		WHERE (m.run_name = "v01_all_run2_pca90" OR m.run_name = "v01_all_run3_pca90")  AND m.k_value = ranked_k.ranked_k_value  AND l.type = "tag"
--         ORDER BY ranked_k.ranked_k_value, m.cluster_id, m.factor_tf_idf desc
-- 	) as j
-- ) as ranked_clusters
-- where ranked_clusters.cluster_rank <= 1 and ranked_clusters.ranked_k_value = 120
-- GROUP BY label_name
-- ORDER BY cluster_rank, label_name;

# top 5 for each cluster for each k
select b.k, avg(b.idf_s) FROM
(
	Select *,  idf(a.uniq_cnt, a.k) as idf_s 
	FROM (
		SELECT rj.ranked_k_value as k, rj.cluster_id, rj.label_name, count(rj.label_name) as uniq_cnt
		FROM ( 
			SELECT * FROM (
				SELECT 
				j.ranked_k_value,
				j.cluster_id, 
				@cluster_rank := if(@current_cluster = j.cluster_id, @cluster_rank  + 1, 1) AS cluster_rank ,
				j.label_name,
				j.factor_tf_idf,
				@current_cluster := j.cluster_id
				FROM ( 
					SELECT  *
					FROM matchings AS m
					INNER JOIN ( 
						SELECT ma.k_value as ranked_k_value
						FROM matchings AS ma
						WHERE (ma.run_name = "v01_all_run2_pca90" OR ma.run_name = "v01_all_run3_pca90") 
						group by ma.k_value
					) as ranked_k on ranked_k.ranked_k_value = m.k_value
					WHERE (m.run_name = "v01_all_run2_pca90" OR m.run_name = "v01_all_run3_pca90")  AND m.k_value = ranked_k.ranked_k_value
					ORDER BY ranked_k.ranked_k_value, m.cluster_id, m.factor_tf_idf desc
				) as j
			) as ranked_clusters
			where ranked_clusters.cluster_rank <= 5
		) as rj
		GROUP BY rj.ranked_k_value, rj.label_name
	) as a
	ORDER BY a.k
) as b
Group by b.k;


SELECT rj.ranked_k_value as k, rj.cluster_id, rj.label_name, rj.factor_tf_idf
FROM ( 
	SELECT * FROM (
		SELECT 
		j.ranked_k_value,
		j.cluster_id, 
		@cluster_rank := if(@current_cluster = j.cluster_id, @cluster_rank  + 1, 1) AS cluster_rank ,
		j.label_name,
		j.factor_tf_idf,
		@current_cluster := j.cluster_id
		FROM ( 
			SELECT  *
			FROM matchings AS m
			INNER JOIN ( 
				SELECT ma.k_value as ranked_k_value
				FROM matchings AS ma
				WHERE (ma.run_name = "v01_all_run2_pca90" OR ma.run_name = "v01_all_run3_pca90") 
				group by ma.k_value
			) as ranked_k on ranked_k.ranked_k_value = m.k_value
			WHERE (m.run_name = "v01_all_run2_pca90" OR m.run_name = "v01_all_run3_pca90")  AND m.k_value = ranked_k.ranked_k_value
			ORDER BY ranked_k.ranked_k_value, m.cluster_id, m.factor_tf_idf desc
		) as j
	) as ranked_clusters
	where ranked_clusters.cluster_rank <= 5
) as rj
WHERE rj.ranked_k_value = 25;



# calculate averages/std for each k over averages of top n factor_tf_idf-scores for each cluster
-- SET @n := 2;
-- SELECT rj.ranked_k_value, 
-- AVG(rj.cluster_label_count),
-- AVG(rj.cluster_size),
-- AVG(rj.factor_tf_idf),
-- STD(rj.factor_tf_idf)
-- FROM ( 
-- 	SELECT 
--     ranked_clusters.cluster_id, 
--     ranked_clusters.ranked_k_value, 
--     c.n_screenshots as cluster_size,
-- 	ranked_clusters.cluster_label_count,
-- 	ranked_clusters.percentage,
-- 	ranked_clusters.factor,
-- 	ranked_clusters.tf,
-- 	ranked_clusters.idf,
-- 	ranked_clusters.tf_idf,
-- 	ranked_clusters.factor_tf_idf
--     FROM (
-- 		SELECT 
--         j.cluster_id,
-- 		j.ranked_k_value, 
-- 		@cluster_rank := if(@current_cluster = j.cluster_id, @cluster_rank  + 1, 1) AS cluster_rank ,
-- 		j.label_name,
--         j.cluster_label_count,
--         j.percentage,
--         j.factor,
--         j.tf,
--         j.idf,
--         j.tf_idf,
-- 		j.factor_tf_idf,
-- 		@current_cluster := j.cluster_id
-- 		FROM ( 
-- 			SELECT  *
-- 			FROM matchings AS m
-- 			INNER JOIN ( 
-- 				SELECT ma.k_value as ranked_k_value
-- 				FROM matchings AS ma
-- 				WHERE (ma.run_name = "v01_all_run2_pca90" OR ma.run_name = "v01_all_run3_pca90")    k / |in wie vielen clustern ist das label in uniq_label|
-- 				group by ma.k_value
-- 			) as ranked_k on ranked_k.ranked_k_value = m.k_value
-- 			WHERE (m.run_name = "v01_all_run2_pca90" OR m.run_name = "v01_all_run3_pca90")  AND m.k_value = ranked_k.ranked_k_value
-- 			ORDER BY ranked_k.ranked_k_value, m.cluster_id, m.factor_tf_idf desc
-- 		) as j
-- 	) as ranked_clusters
--     inner join clusters as c on c.k_value = ranked_clusters.ranked_k_value and c.cluster_id = ranked_clusters.cluster_id
-- 	where ranked_clusters.cluster_rank <= @n
-- ) as rj
-- GROUP BY rj.ranked_k_value; # additionally group by cluster and select rj.cluster_id to show average values for each cluster

# rank clusters for a specific k
-- SELECT * ,#m.cluster_id, m.k_value, m.label_name, m.factor_tf_idf, 
-- 	@cluster_rank := if(@current_cluster = m.cluster_id, @cluster_rank  + 1, 1) AS cluster_rank ,
-- 	@current_cluster := m.cluster_id
-- 	FROM matchings AS m
-- 	WHERE m.run_name = "v01_all_run2_pca90" and m.k_value = 90 and m.cluster_id=4
-- 	ORDER BY m.cluster_id, m.factor_tf_idf desc;

# rank all k's
-- SELECT ma.k_value,
-- @k_rank := if(@current_run = ma.run_name, @k_rank + 1, 1) as k_rank,
-- @current_run := ma.run_name
-- FROM matchings AS ma
-- WHERE ma.run_name = "v01_all_run2_pca90" 
-- group by ma.k_value
-- ORDER BY ma.k_value asc;


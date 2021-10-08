SELECT distinct 
m.cluster_id, m.k_value,
label_name, 
l.count as total_count, 
c.n_screenshots as cluster_size, 
cluster_label_count, 
percentage, factor, tf, idf, tf_idf, factor_tf_idf
FROM clustering_db.matchings m
inner join labels l on l.name = m.label_name
inner join clusters c on c.run_name=m.run_name and m.cluster_id=c.cluster_id and m.k_value=c.k_value
ORDER BY factor_tf_idf desc;

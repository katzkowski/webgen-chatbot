USE clustering_db; 

SET SQL_SAFE_UPDATES=0; -- disable

-- update labels as lbls
-- inner join ( select la.id, Count(*) as total_label_count
--     from screenshots as s
--     inner join websites as w on w.url=s.page_url
--     inner join website_labels as wl on w.id=wl.website_id
--     inner join labels as la on wl.label_id=la.id
--     group by la.name
-- ) as tlc on tlc.id=lbls.id
-- SET lbls.count = tlc.total_label_count
-- WHERE lbls.id = tlc.id;

SET SQL_SAFE_UPDATES=1; -- enable
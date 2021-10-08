select l.name, l.type, Count(*)
from screenshots as s
inner join websites as w on w.url=s.page_url
inner join website_labels as wl on w.id=wl.website_id
inner join labels as l on wl.label_id=l.id
group by l.name
having count(*) > 100
order by count(*) desc;

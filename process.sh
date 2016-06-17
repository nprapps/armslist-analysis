#!/bin/bash
mkdir -p output

echo "Generate state distribution jun12-jun15"
psql armslist -c "COPY (
SELECT l.state, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
GROUP BY l.state
ORDER BY count desc
) to '`pwd`/output/state_distribution_jun12_15.csv' WITH CSV HEADER;"

echo "Generate semiautomatic state distribution jun12-jun15"
psql armslist -c "COPY (
SELECT l.state, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
AND l.action = 'Semi-automatic'
GROUP BY l.state
ORDER BY count desc
) to '`pwd`/output/semiautomatic_state_distribution_jun12_15.csv' WITH CSV HEADER;"

echo "Generate map data jun12-jun15"
psql armslist -c "COPY (
SELECT l.geo_address, l.latitude, l.longitude, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
GROUP BY l.geo_address, l.latitude, l.longitude
ORDER BY count desc
) to '`pwd`/output/map_counts_jun12_15.csv' WITH CSV HEADER;"

echo "Generate semiautomatic map data jun12-jun15"
psql armslist -c "COPY (
SELECT l.geo_address, l.latitude, l.longitude, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
AND l.action = 'Semi-automatic'
GROUP BY l.geo_address, l.latitude, l.longitude
ORDER BY count desc
) to '`pwd`/output/semiautomatic_map_counts_jun12_15.csv' WITH CSV HEADER;"


echo "Generate map data without states jun12-jun15"
psql armslist -c "COPY (
(SELECT l.geo_address, l.latitude, l.longitude, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
AND l.geo_address != l.state
GROUP BY l.geo_address, l.latitude, l.longitude
ORDER BY count desc)
UNION
(SELECT l.geo_address, l.latitude, l.longitude, COUNT(*) as count FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
AND l.geo_address = l.state AND l.state IN ('Delaware', 'Maine', 'Massachusetts', 'New Jersey', 'Rhode Island', 'South Dakota')
GROUP BY l.geo_address, l.latitude, l.longitude
ORDER BY count desc)
) to '`pwd`/output/map_counts_wo_states_jun12_15.csv' WITH CSV HEADER;"



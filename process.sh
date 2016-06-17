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

echo "Generate map data geocoded by nominatim without states jun12-jun15"
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
) to '`pwd`/output/map_counts_wo_states_nominatim_jun12_15.csv' WITH CSV HEADER;"

echo "total listings jun12-jun15"
psql armslist -c "COPY (
SELECT COUNT(*) FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
) to '`pwd`/output/overall_listings_jun12_15.csv' WITH CSV HEADER;"

echo "semi-automatic listings jun12-jun15"
psql armslist -c "COPY (
SELECT COUNT(*) FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
AND l.action = 'Semi-automatic'
) to '`pwd`/output/semi-automatic_listings_jun12_15.csv' WITH CSV HEADER;"

echo "private vs premium listings jun12-jun15"
psql armslist -c "COPY (
SELECT l.party, COUNT(*) FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
GROUP BY l.party
) to '`pwd`/output/private_listings_jun12_15.csv' WITH CSV HEADER;"

echo "registered vs unregistered listings jun12-jun15"
psql armslist -c "COPY (
SELECT l.registered, COUNT(*) FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
GROUP BY l.registered
) to '`pwd`/output/unregistered_listings_jun12_15.csv' WITH CSV HEADER;"

echo "listings grouped by action jun12-jun15"
psql armslist -c "COPY (
SELECT l.action, COUNT(*) FROM listings l
WHERE listed_date BETWEEN to_date('2016-06-12','YYYY-MM-DD') AND to_date('2016-06-15','YYYY-MM-DD')
GROUP BY l.action
) to '`pwd`/output/byaction_listings_jun12_15.csv' WITH CSV HEADER;"

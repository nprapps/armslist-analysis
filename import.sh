#!/bin/bash

# setup our database
echo "Create database"
dropdb --if-exists armslist
createdb armslist

# get listings csv in the db
echo "Import listings geocoded with nominatim to database"
psql armslist -c "CREATE TABLE listings (
  url varchar,
  post_id varchar,
  title varchar,
  listed_date date,
  price_str varchar,
  price_num numeric,
  location varchar,
  city varchar,
  state varchar,
  state_ap varchar,
  state_usps varchar,
  description varchar,
  registered boolean,
  category varchar,
  manufacturer varchar,
  caliber varchar,
  action varchar,
  firearm_type varchar,
  party varchar,
  img varchar,
  geo_address varchar,
  latitude decimal(9,6),
  longitude decimal(9,6)
);"
psql armslist -c "COPY listings FROM '`pwd`/data/listings-clean-nominatim.csv' DELIMITER ',' CSV HEADER;"

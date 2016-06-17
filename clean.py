#!/usr/bin/env python
# coding: utf-8
import os
from csvkit.py2 import CSVKitDictReader, CSVKitDictWriter
from mapbox import Geocoder
from time import sleep


# GLOBAL SETTINGS
cwd = os.path.dirname(__file__)
INPUT_PATH = os.path.join(cwd, 'data')
INPUT_FILE = 'listings-2016-06-16-0800'
CACHE_FILE = 'geocoded-cache'
OUTPUT_FILE = 'listings-clean'
HEADER = ["url", "post_id", "title", "listed_date", "price_str", "price_num",
          "location", "city", "state", "description", "registered", "category",
          "manufacturer", "caliber", "action", "firearm_type", "party", "img",
          "geo_address", "latitude", "longitude"]
CACHE_HEADER = ["address", "latitude", "longitude"]

# LIMIT CONDITIONS FOR TESTING
LIMIT = False
LIMIT_SAMPLE = 5000

# MAPBOX API KEY
MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY', 'key')

cache = {}


def persist_cache():
    """
    Persist cache to disk
    """
    with open('%s/%s.csv' %
              (INPUT_PATH, CACHE_FILE), 'w') as fout:
        writer = CSVKitDictWriter(fout, fieldnames=CACHE_HEADER)
        writer.writeheader()
        for k, v in cache.iteritems():
            row = {'address': k, 'latitude': v[1], 'longitude': v[0]}
            writer.writerow(row)


def format_address(row=None):
    """
    Format the addresses into something that may be geocoded
    """
    address = None
    if row['city']:
        # if city is a state acronym include last part of location
        # TODO: fix this on the scraper
        if (len(row['city']) == 2 and row['city'] == row['city'].upper()):
            bits = row['location'].split(',')
            city_part = bits[len(bits) - 1].strip()
            # Geocode city and state
            address = "%s %s, %s" % (city_part, row['city'], row['state'])
        else:
            # Geocode city and state
            address = "%s, %s" % (row['city'], row['state'])
    else:
        # Geocode state
        address = "%s" % (row['state'])
    return address


def geocode(row=None, geocoder=None):
    """geocode based on address"""
    # Check for places
    row['latitude'] = None
    row['longitude'] = None

    address = format_address(row)
    if address not in cache:
        # Give mapBox some rest
        sleep(0.5)
        geo_resp = geocoder.forward(address)
        geo_data = geo_resp.geojson()
        # If mapbox did not return results view response and leave blank
        if not geo_data['features']:
            print "address %s not found by mapbox" % address
            print "location: %s, city: %s, state: %s" % (row['location'],
                                                         row['city'],
                                                         row['state'])
            cache[address] = [None, None]
            return
        # Get the top hit
        top_hit = geo_data['features'][0]
        coordinates = top_hit['geometry']['coordinates']
    else:
        coordinates = cache[address]

    # Store into cache for reuse
    cache[address] = coordinates

    # update geolocation to the record
    if coordinates:
        row['geo_address'] = address
        row['latitude'] = coordinates[1]
        row['longitude'] = coordinates[0]


def process_armlist():
    # Create output files folder if needed
    OUTPUT_PATH = INPUT_PATH
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    # Initialize geocoder
    geocoder = Geocoder(access_token=MAPBOX_API_KEY)

    with open('%s/%s.csv' %
              (INPUT_PATH, OUTPUT_FILE), 'w') as fout:
        writer = CSVKitDictWriter(fout, fieldnames=HEADER,
                                  extrasaction='ignore')
        writer.writeheader()
        with open('%s/%s.csv' % (INPUT_PATH, INPUT_FILE), 'r') as f:
            reader = CSVKitDictReader(f)
            count = 0
            for row in reader:
                count += 1
                if count % 1000 == 0:
                    print "processed %s records" % count
                if LIMIT and (count >= LIMIT_SAMPLE):
                    break

                # Clean description
                row['description'] = row['description'].replace("\n", "\\n")
                # Clean listed date to insert into postgres
                row['listed_date'] = row['listed_date'].replace("Listed On: ",
                                                                "")
                # Split numeric vs string prices
                try:
                    row['price_num'] = int(row['price'].replace(",", ""))
                except ValueError:
                    row['price_str'] = row['price']

                # Geocode
                geocode(row, geocoder)
                # Write to csv file
                writer.writerow(row)
            print('finished processing {}.csv'.format(INPUT_FILE))

    # Persist cache file to disk
    persist_cache()


def load_geocoded_cache():
    try:
        with open('%s/%s.csv' % (INPUT_PATH, CACHE_FILE), 'r') as f:
            reader = CSVKitDictReader(f)
            for row in reader:
                cache[row['address']] = [row['longitude'], row['latitude']]
    except IOError:
        # No cache file found
        pass


def run():
    load_geocoded_cache()
    process_armlist()


if __name__ == '__main__':
    run()

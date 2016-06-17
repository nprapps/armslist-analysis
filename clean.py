#!/usr/bin/env python
# coding: utf-8
import os
from csvkit.py2 import CSVKitDictReader, CSVKitDictWriter
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim
from time import sleep


# GLOBAL SETTINGS
cwd = os.path.dirname(__file__)
INPUT_PATH = os.path.join(cwd, 'data')
INPUT_FILE = 'armslist-listings-2016-06-16'
CACHE_FILE = 'geocoded-cache-nominatim'
STATE_FILE = 'states-normalized'
OUTPUT_FILE = 'listings-clean-nominatim'
HEADER = ["url", "post_id", "title", "listed_date", "price_str", "price_num",
          "location", "city", "state", "state_ap", "state_usps",
          "description", "registered", "category",
          "manufacturer", "caliber", "action", "firearm_type", "party", "img",
          "geo_address", "latitude", "longitude"]

CACHE_HEADER = ["address", "latitude", "longitude"]

# LIMIT CONDITIONS FOR TESTING
LIMIT = False
LIMIT_SAMPLE = 50

cache = {}
states = {}


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


def clean(row=None):
    """
    Clean dataset:
        - Clean description
        - Split Price into numeric or not
        - Remove prefix for the date
        - Normalize state
    """
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

    # Normalize state
    try:
        state_norm = states[row['state']]
        row['state_ap'] = state_norm[0]
        row['state_usps'] = state_norm[1]
    except KeyError:
        print "did not find %s" % (row['state'])


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


def geocode_nominatim(row=None, geocoder=None):
    """geocode based on address"""
    # Check for places
    row['latitude'] = None
    row['longitude'] = None

    address = format_address(row)
    if address not in cache:
        # Give mapBox some rest
        sleep(2)
        query = {'country': 'us'}
        bits = address.split(',')
        if (len(bits) > 1):
            # State and city
            query['city'] = bits[0].strip()
            query['state'] = bits[1].strip()
        else:
            # Only state
            query['state'] = address

        try:
            location = geocoder.geocode(query, exactly_one=True, timeout=2)
        except GeocoderServiceError:
            location = None

        if location:
            coordinates = [location.longitude, location.latitude]
        else:
            # If we did not find a location set to None and cache to avoid
            # hitting the same error again
            coordinates = [None, None]
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
    geocoder = Nominatim()

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

                # Clean data
                clean(row)
                # Geocode
                # geocode(row, geocoder)
                geocode_nominatim(row, geocoder)
                # Write to csv file
                writer.writerow(row)
            print('finished processing {}.csv'.format(INPUT_FILE))


def load_state_normalized():
    """ State with AP and USPS abbreviations"""
    try:
        with open('%s/%s.csv' % (INPUT_PATH, STATE_FILE), 'r') as f:
            reader = CSVKitDictReader(f)
            for row in reader:
                states[row['name']] = [row['ap'], row['usps']]
    except IOError:
        # No cache file found
        pass


def load_geocoded_cache():
    """ Load persisted geocoded locations"""
    try:
        with open('%s/%s.csv' % (INPUT_PATH, CACHE_FILE), 'r') as f:
            reader = CSVKitDictReader(f)
            for row in reader:
                cache[row['address']] = [row['longitude'], row['latitude']]
    except IOError:
        # No cache file found
        pass


def run():
    try:
        load_state_normalized()
        load_geocoded_cache()
        process_armlist()
    except Exception, e:
        print "An exception has occured %s" (e)
    finally:
        # Always persist cache file to disk
        persist_cache()


if __name__ == '__main__':
    run()

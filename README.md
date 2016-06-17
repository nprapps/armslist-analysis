Copyright 2016 NPR. All rights reserved. No part of these materials may be reproduced, modified, stored in a retrieval system, or retransmitted, in any form or by any means, electronic, mechanical or otherwise, without prior written permission from NPR.

(Want to use this code? Send an email to nprapps@npr.org!)

# Armslist analysis

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Requirements](#requirements)
* [Installation](#installation)
* [Run the project](#run)
* [What to expect](#what-to-expect)
* [Postgres DB analysis](#db-analysis)

## What is this? <a id="what-is-this"></a>

Armslist-analysis was made to clean and summarize data from Armslist.com, a site used as a marketplace for buying and selling guns.

## Assumptions <a id="assumptions"></a>

The following things are assumed to be true in this documentation.
* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have virtualenv and virtualenvwrapper installed and working.

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

This code should work fine in most recent versions of Linux, but package installation and system dependencies may vary.

## Installation <a id="installation"></a>

Clone the project:

```
git clone git@github.com:nprapps/armslist-analysis.git
cd armslist-analysis
```

## Run the project <a id="run"></a>

Create a virtual environment and install the requirements:

```
mkvirtualenv armslist-analysis
pip install –r requirements.txt
```

Then grab a dump of the armlist dataset in csv format and place it into the data folder

The next script will try to geocode the data based on the city and state of each listing, we use [Nominatim geocoding service](http://wiki.openstreetmap.org/wiki/Nominatim) access through the [geopy](http://geopy.readthedocs.io/en/latest/#) library to perform that task.

Run the script to clean and geocode the data:

```
./clean.py
```

## What to expect <a id="what-to-expect"></a>

The script will create an on-memory geocode cache to try to minimize the hits to the actual MAPBOX API.

Running script will make two csv files:

* `data/listings-clean.csv` is the bulk of the data with geolocation included. Each row represents a listing and the associated details.
* `data/geocoded-cache.csv` is the geocoded cache persisted to disk for future runs of the script

## Import to DB and summarize <a id="db-analysis"></a>

We created a script to insert the cleaned data into a Postgres database for further analysis

```
./import.sh
```

After the script has successfully created the database tables, we can run the script that will generate the output data that has been used in our own articles

```
./process.sh
```

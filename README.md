# artdatabanken-utils

Assorted tools to interact with [Artdatabankens](https://api-portal.artdatabanken.se/) API:s. As of February 13, there are five API:s described here: https://api-portal.artdatabanken.se/docs/services.

# Requirements

It is developed with Python 3.6. The current dependencies are to Python3 standard modules and 'requests'. See below.

# About the utils

There are two main components:

* **obsapi.py** is a Python module for invoking the "Species Observation System API".
* **adb-get.py** is a Python CLI-program for making calls to the "Artfakta - Species information API", the "Species Observation System API" and an older "Observations Sandbox API".

Note that use of all of the above API:S require you to have API-keys for each API.

There is also [Postman API collections resource]("artdatbankens-apis.postman.json") that can be imported into Postman for trying out some API calls.

# Development

Set up the development environment with:

 1. Clone the git repo.
 2. Create a virtual env:
```
$ virtualenv -p python3 env
```
 3. Jump into the virtual env:
```
$ source env/bin/activate
```
 4. Install dependent packages with:
```
$ pip install -r requirements.txt
```
 5. Start hacking!

# Usage

If you want to know what `adb-get.py` can do, without reading the source code, run it with:
```
$ ./adb-get.py -h
```

To get the first 200 observations of Tajgasångare or Yellow-browed warbler (*Phylloscopus inornatus*), with Artdatabanken taxon id 205835, since 1900-01-01 do:
```
$ ./adb-get.py --get-observations --taxon-id=205835
```

Or get them by taxon name with:
```
$ ./adb-get.py --get-observations --taxon-name=Tajgasångare
```

You can pass your API keys as options with the `--species-api-key` and the `--observations-api-key`, but it is easier to set them as environment variables:
```
$ export ADB_SPECIES_API_KEY=<YOUR-SPECIES-API-KEY>
$ export ADB_OBSERVATIONS_SANDBOX_API_KEY=<YOUR-OBSERVATIONS-SANDBOX-API-KEY>
$ export ADB_OBSERVATIONS_API_KEY=<YOUR_OBSERVATIONS-API-KEY>
```
so you don't have to provide them as options each time you invoke `adb-get.py`.

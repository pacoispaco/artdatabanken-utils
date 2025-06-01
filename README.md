# artdatabanken-utils

This is a personal project to investigate what can be and what can't be done with with [Artdatabankens](https://api-portal.artdatabanken.se/) API:s. As of February 13, 2025, there are five API:s described here: https://api-portal.artdatabanken.se/docs/services.

Artportalen is a public Swedish crowd science service for registering species observations. It is developed and run by the Swedish Species Information Centre" at the Swedish University of Agricultural Sciences (SLU - Sveriges Lantbruksuniversitet). It 

## Requirements

It is developed with Python 3. The current dependencies are to Python3 standard modules and  the 'requests' module.

In order to call the Artdatabanken API:s you need to register and account there and get API keys for the API:s you intend to use. These tools currently use the Obeservations API and the Species API.

## To get started

Clone the repo:
```bash
git clone URL-TO-REPO
```

Create a virtual environment:
```bash
virtualenv -p python3 env
```

Install the requirements:
```bash
pip install -r requirements.txt
```

## Trying out the Artportalen API:s

You can always try out the API:s with Postman or command line tools like curl, wget or httpie.

This repo contains a [Postman API collections resource]("artdatbankens-apis.postman.json") that can be imported into Postman for trying out some API calls.

The repo also contain a simple command line program **apget.py** which can be used to try out, learn and get data from the Artportalen API:s. See below.

## Design

There is a module **artportalen.py** which contains classes and methods for calling the Artportalen API:s. This module is intended to be used as a reusable and simple Python interface to the API:s. It replaces a first attempt called **obsapi.py**.

The command line program **apget.py** uses the **artportalen.py** module, and is used when developing that module. It also showcases how that module can, and is intended to be used. It replaces a first attempt **adb_get.py**.

### Notes on apget.py

The program uses the module **obsapi**. You need two API keys to be set as the environment variables `ADB_OBSERVATIONS_API_KEY` and `ADB_SPECIES_API_KEY` for the program to work. Make sure you are in the local virtual environment and run:

```bash
(env) $ export ADB_OBSERVATIONS_API_KEY=<API-KEY-1>
(env) $ export ADB_SPECIES_API_KEY=<API-KEY-2>
(env) $ ./apget.py
```

If you want to know what `apget.py` can do, run it with:

```bash
$ ./apget.py -h
usage: apget.py [-h] [-v] [-c CONF_FILE_PATH] [--taxon-id TAXON_ID]
                [--taxon-name TAXON_NAME] [--pretty-print] [-V] [-g] [-s]
                [-r] [--from-date FROM_DATE] [--to-date TO_DATE]
                [--offset OFFSET] [--limit LIMIT]

CLI-program for getting stuff from the Artdatabanken API:s. Note that you
must set the two API keys as environment variables. Ie: export
ADB_SPECIES_API_KEY=<API-KEY> export ADB_OBSERVATIONS_API_KEY=<API-KEY>

options:
  -h, --help            show this help message and exit
  -v, --verbose         print info about what's going on [False].
  -c CONF_FILE_PATH, --conf-file-path CONF_FILE_PATH
                        Configuration file path [adb-get.conf].
  --taxon-id TAXON_ID   Artdatabanken's taxon id
  --taxon-name TAXON_NAME
                        Artdatabanken's taxon name in Swedish
  --pretty-print        Pretty print all info.
  -V, --get-api-versions
                        Get API versions.
  -g, --get-observations
                        Get observations [False]
  -s, --show-search-filter
                        Show the search filter used [False]. Use with '-g'
  -r, --sort-reverse    Sort observations in reverse order [False]
  --from-date FROM_DATE
                        From date [1900-01-01T00:00]
  --to-date TO_DATE     To date [2025-06-01T12:10]
  --offset OFFSET       Offset [0]
  --limit LIMIT         Limit [200]
```

To get observations use the `-g/--get-observations` option:

```
$ ./apget.py -g
```
That will return the first 200 observations, givet the default search criteria. 

To get the first 200 observations of Tajgasångare or Yellow-browed warbler (*Phylloscopus inornatus*) since 1900-01-01, do:

```
$ ./apet.py --g --taxon-name=Tajgasångare
```

You can also use the taxon-id if you know that (for Tajgasångare or Yellow-browed warbler it is 205835):

```
$ ./apget.py --g --taxon-id=205835
```

### Notes on artportalen.py

This module has classes and methods for interacting with the Artportalen API:s. The core classes are:

* **SpeciesAPI**. Represents the Artportalen SpeciesAPI and has methods for interacting with that API.
* **ObservationsAPI**. Represents the Artportalen ObservationsAPI and has methods for interacting with that API.
* **SearchFilter**. Represents the search filter to use as request body when doing a HTTP GET on the search resource in the Artportalen ObservationsAPI.

It also contains these data model classes:

* **Taxon**.
* **Observation**.
* **Person**.

The documentation on the Artportalen API:s is somewhat lacking, and the design of the API:s is not resource-oriented (HTTP/REST-ish), but rather method-oriented (OO- and SOAP-ish). There is no proper introductory description of using the API:s, and there is incomplete documentation on some of the request parameters and the JSON-structures used. This does not provide a good developer experience and it enforces a cumbersome trial-and-error approach to using the API.

As an example, the important HTTP resource (method) **Observations_ObservationsBySearch** in the ObservationsAPI, returns observations based on a search filter in JSON format sent in the HTTP POST request and a few request paramaters. Two of those request parameters are "sortBy" and "sortOrder", which affect the order of the returned observations. The only description of "sortBy" is that it is a string which specifies which "Field to sort by.". Nothing more. By trial and error I managed to figure out that "fields" refers to the named JSON-attributes in the individual "Observation" JSON-objects returned in the response object. So to sort the returned observations by date, I could use the request parameter `sortBy="event.startDate"`.


# artdatabanken-utils

This is a personal project to investigate what can be and what can't be done with with [Artdatabankens](https://api-portal.artdatabanken.se/) API:s. As of February 13, 2025, there are five API:s described here: https://api-portal.artdatabanken.se/docs/services.

Artportalen is a public Swedish crowd science service for registering species observations. It is developed and run by the Swedish Species Information Centre" at the Swedish University of Agricultural Sciences (SLU - Sveriges Lantbruksuniversitet).

# Requirements

It is developed with Python 3. The current dependencies are to Python3 standard modules and  the 'requests' module.

In order to call the Artdatabanken API:s you need to register and account there and get API keys for the API:s you intend to use. These tools currently use the Obeservations API and the Species API.

# To get started

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

# Trying out the Artportalen API:s

You can always try out the API:s with Postman or command line tools like curl, wget or httpie.

This repo contains a [Postman API collections resource]("artdatbankens-apis.postman.json") that can be imported into Postman for trying out some API calls.

The repo also contain a simple command line program **apget.py** which can be used to try out, learn and get data from the Artportalen API:s. See below.

# Design

There is a module **artportalen.py** which contains a few methods for calling the Artportalen API:s. This module is intended to be reusable. It replaces a first attempt called **obsapi.py**.

The command line program **apget.py** uses the *artportalen.py** module, and is used when developing that module. It also showcases how the module can and is intended to be used. It replaces a first attempt **adb_get.py**.

## apget.py

The program uses the module **obsapi**. You need two API keys to be set as the environment variables `ADB_OBSERVATIONS_API_KEY` and `ADB_SPECIES_API_KEY` for the program to work. Make sure you are in the local virtual environment and run:

```bash
(env) $ export ADB_OBSERVATIONS_API_KEY=<API-gramKEY-1>
(env) $ export ADB_SPECIES_API_KEY=<API-KEY-2>
(env) $ ./apget.py
```

If you want to know what `apget.py` can do run it with:
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

# artdatabanken-utils

Assorted tools to interact with [Artdatabankens](https://api-portal.artdatabanken.se/) API:s.

# Requirements

It is developed with Python 3.6. The current dependencies are to Python3 standard modules and 'requests'. See below.

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

If you want to know what `adb-get.py` can do, without reading the source code run it with:
```
$ ./adb-get.py -h
```

where <YOUR-API-KEY> is the API subscription key you obtained when registering
for an API account with Artdatabanken.

To get the first 200 observations of Tajgasångare since 1900-01-01 do:
```
$ ./adb-get.py -k<YOUR-API-KEY> --get-observations --taxon-id=205835 -v
```

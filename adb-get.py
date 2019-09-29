#!/usr/bin/env python3

"""This is a CLI program that gets stuff from the Artdatabanken API:s and prints it to stdout."""

import sys
import argparse
import os
import os.path
from datetime import datetime
import requests
import pprint
#from requests_oauthlib import OAuth2Session

# Constants
DEFAULT_CONF_FILE_PATH = 'adb-get.conf'
DEFAULT_FROM_DATE_RFC3339 = '1900-01-01T00:00'
ADB_SPECIES_API_KEY_ENV_NAME = 'ADB_SPECIES_API_KEY'
ADB_OBSERVATIONS_API_KEY_ENV_NAME = 'ADB_OBSERVATIONS_API_KEY'
ADB_API_ROOT_URL = 'https://api.artdatabanken.se'
ADB_SPECIES_API_PATH = '/information/v1/speciesdataservice/v1/'
ADB_OBSERVATIONS_API_PATH = '/observations-r/v2/'
ADB_OBSERVATIONS_API_SANDBOX_PATH = '/sandbox-observations-r/v2/'


def auth_headers(api_key, auth_token=None):
    """Returns a dictionary of authentication headers."""
    h = {'Ocp-Apim-Subscription-Key': api_key}
    if auth_token:
        h['Authorization'] = 'Bearer {%s}' % (auth_token)
    return h


def species_api_key():
    """Value of the Species API key environment variable if it exists, otherwise None."""
    if ADB_SPECIES_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_SPECIES_API_KEY_ENV_NAME]
    else:
        return None


def observations_api_key():
    """Value of the Observations API key environment variable if it exists, otherwise None."""
    if ADB_OBSERVATIONS_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_OBSERVATIONS_API_KEY_ENV_NAME]
    else:
        return None


def get_taxon_id_by_name(args, species_url, taxon_name):
    """Artdatabanken's taxon id for the taxon with the given `taxon_name`. Returns None if not found. """
    url = '%s%s' % (species_url, 'speciesdata/search?searchString=%s' % (taxon_name))
    r = requests.get(url, headers=auth_headers(args.species_api_key))
    if args.verbose:
        print('GET %s' % url)
        print('HTTP Status code: %s' % (r.status_code))
        print('HTTP Response headers:')
        print(r.headers)
        print('HTTP Response body:')
    for d in r.json():
        if d['swedishName'] == taxon_name.lower():
            return d['taxonId']
    return None


def get_taxon_by_id(args, species_url, taxon_id):
    """Artdatabanken's taxon data for the taxon with the given `taxon_id`. Returns None if not found. """
    url = '%s%s' % (species_url, 'speciesdata?taxa=%s' % (taxon_id))
    r = requests.get(url, headers=auth_headers(args.species_api_key))
    if args.verbose:
        print('GET %s' % url)
        print('HTTP Status code: %s' % (r.status_code))
        print('HTTP Response headers:')
        print(r.headers)
        print('HTTP Response body:')
    if r.json() == []:
        return None
    else:
        return r.json()


def today_RFC3339():
    """Today as an RFC 3339 / ISO 8601 date and time string, in minute resolution."""
    today = datetime.now()
    return today.isoformat(timespec='minutes')


def main():
    parser = argparse.ArgumentParser(description='''CLI-program for getting stuff from the Artdatabanken API:s.''')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False].")
    parser.add_argument('-c', '--conf-file-path', default=DEFAULT_CONF_FILE_PATH,
                        help="Configuration file path [%s]." % (DEFAULT_CONF_FILE_PATH))
    parser.add_argument('-p', '--ping-the-apis', action='store_true', default=False,
                        help="Ping the Artportalen API:s to check authentication and that it is alive.")
    parser.add_argument('--species-api-key', default=species_api_key(),
                        help="Species API authentication (subscription) key [value of environment variable %s]" %
                        (ADB_SPECIES_API_KEY_ENV_NAME))
    parser.add_argument('--observations-api-key', default=observations_api_key(),
                        help="Observations API authentication (subscription) key [value of environment variable %s]" %
                        (ADB_OBSERVATIONS_API_KEY_ENV_NAME))
    parser.add_argument('--use-production-api', action='store_true', default=False,
                        help="Use the production (and not the sandbox)) API [False]")
    parser.add_argument('--taxon-id',
                        help="Artdatabanken's taxon id")
    parser.add_argument('--taxon-name',
                        help="Artdatabanken's taxon name in Swedish")
    parser.add_argument('--get-observations', action='store_true', default=False,
                        help="Get observations [False]")
    parser.add_argument('--from-date', default=DEFAULT_FROM_DATE_RFC3339,
                        help="From date [%s]" % (DEFAULT_FROM_DATE_RFC3339))
    s = today_RFC3339()
    parser.add_argument('--to-date', default=s,
                        help="To date [%s]" % (s))
    parser.add_argument('--offset', default=0,
                        help="Offset [0]")
    parser.add_argument('--limit', default=200,
                        help="Limit [200]")
    args = parser.parse_args()
    species_url = '%s%s' % (ADB_API_ROOT_URL, ADB_SPECIES_API_PATH)
    if args.use_production_api:
        observations_url = '%s%s' % (ADB_API_ROOT_URL, ADB_OBSERVATIONS_API_PATH)
    else:
        observations_url = '%s%s' % (ADB_API_ROOT_URL, ADB_OBSERVATIONS_API_SANDBOX_PATH)
    if not args.species_api_key:
        print("Error: No Species API key provided (--species-api-key)")
        sys.exit(1)
    if not args.observations_api_key:
        print("Error: No Observations API key provided (--observations-api-key)")
        sys.exit(2)
    if args.ping_the_apis:
        ping_url = '%s%s' % (species_url, 'speciesdata/search?searchString=Tajgasångare')
        r = requests.get(ping_url, headers=auth_headers(args.species_api_key))
        print('GET %s' % ping_url)
        print('HTTP Status code: %s' % (r.status_code))
        if args.verbose:
            print('HTTP Response headers:')
            print(r.headers)
            print('HTTP Response body:')
        if r.status_code == 200:
            print("ok.")
        else:
            print("Failed.")
        if args.verbose:
            pprint.pprint(r.json())
        ping_url = '%s%s' % (observations_url, 'environment')
        r = requests.get(ping_url, headers=auth_headers(args.observations_api_key))
        print('GET %s' % ping_url)
        print('HTTP Status code: %s' % (r.status_code))
        if args.verbose:
            print('HTTP Response headers:')
            print(r.headers)
            print('HTTP Response body:')
        if r.status_code == 200:
            print("ok.")
        else:
            print("Failed.")
        if args.verbose:
            pprint.pprint(r.json())
        sys.exit(0)
    if args.get_observations:
        if not args.taxon_id:
            if not args.taxon_name:
                print("Error: No taxon id (--taxon-id) or taxon name (--taxon-name) specified.")
                sys.exit(2)
            else:
                taxon_id = get_taxon_id_by_name(args, species_url, args.taxon_name)
                if not taxon_id:
                    print("Error: No taxon with name '%s' found in Artdatabankens Species API." % (args.taxon_name))
                    sys.exit(3)
        else:
            taxon_id = args.taxon_id
        url = '%s%s' % (observations_url,
                        'sightings?taxonId=%s&dateFrom=%s&dateTo=%s&offset=%s&limit=%s' % (
                            taxon_id,
                            args.from_date,
                            args.to_date,
                            args.offset,
                            args.limit))
        r = requests.get(url, headers=auth_headers(args.observations_api_key))
        if args.verbose:
            print('GET %s' % url)
            print('HTTP Status code: %s' % (r.status_code))
            print('HTTP Response headers:')
            print(r.headers)
            print('HTTP Response body:')
        pprint.pprint(r.json())
        sys.exit(0)
    if args.taxon_id:
        t = get_taxon_by_id(args, species_url, args.taxon_id)
        if t:
            pprint.pprint(t)
        else:
            print("Error: No taxon with id '%s' found in Artdatabanken's Species API" % (args.taxon_id))
            sys.exit(3)
        sys.exit(0)
    if args.taxon_name:
        taxon_id = get_taxon_id_by_name(args, species_url, args.taxon_name)
        if not taxon_id:
            print("Error: No taxon with name '%s' found in Artdatabanken's Species API." % (args.taxon_name))
            sys.exit(4)
        t = get_taxon_by_id(args, species_url, taxon_id)
        pprint.pprint(t)
        sys.exit(0)


if __name__ == '__main__':
    main()

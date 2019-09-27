#!/usr/bin/env python3

"""This is a CLI program that gets stuff from Artdatabanken's API and prints it to stdout."""

import sys
import argparse
import os
import os.path
from datetime import date
import requests
import pprint
#from requests_oauthlib import OAuth2Session

# Constants
DEFAULT_CONF_FILE_PATH = 'ap-get.conf'
AP_API_KEY_ENV_NAME = 'AP-API-KEY'
AP_API_ROOT_URL = 'https://api.artdatabanken.se'
AP_API_OBSERVATIONS_PATH = '/observations-r/v2/'
AP_API_SANDBOX_OBSERVATIONS_PATH = '/sandbox-observations-r/v2/'


def auth_headers(api_key, auth_token=None):
    """Returns a dictionary of authentication headers."""
    h = {'Ocp-Apim-Subscription-Key': api_key}
    if auth_token:
        h['Authorization'] = 'Bearer {%s}' % (auth_token)
    return h


def ap_api_key():
    """Returns the value of the API key environment variable if it exists, otherwise None."""
    if AP_API_KEY_ENV_NAME in os.environ:
        return os.environ[AP_API_KEY_ENV_NAME]
    else:
        return None


def today_RFC3339():
    today = date.today()
    return today.strftime("%Y-%m-%d")

def main():
    parser = argparse.ArgumentParser(description='''CLI-program for getting stuff from Ardatabanken's API.''')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False].")
    parser.add_argument('-c', '--conf-file-path', default=DEFAULT_CONF_FILE_PATH,
                        help="Configuration file path [%s]." % (DEFAULT_CONF_FILE_PATH))
    parser.add_argument('-p', '--ping-the-api', action='store_true', default=False,
                        help="Ping the Artportalen API to check authentication and that it is alive and get info on current user of the API.")
    parser.add_argument('-k', '--api-key', default=ap_api_key(),
                        help="API authentication (subscription) key [value of environment variable %s]" % (AP_API_KEY_ENV_NAME))
    parser.add_argument('--use-production-api', action='store_true', default=False,
                        help="Use the production (and not the sandbox)) API [False]")
    parser.add_argument('--taxon-id',
                        help="Artdatabankens Taxon id ")
    parser.add_argument('--get-observations', action='store_true', default=False,
                        help="Get observations [False]")
    parser.add_argument('--from-date', default="1900-01-01",
                        help="From date [1900-01-01]")
    parser.add_argument('--to-date', default=today_RFC3339(),
                        help="To date [%s]" % (today_RFC3339()))
    parser.add_argument('--offset', default=0,
                        help="Offset [0]")
    parser.add_argument('--limit', default=200,
                        help="Limit [200]")
    args = parser.parse_args()
    if args.use_production_api:
        api = AP_API_OBSERVATIONS_PATH
    else:
        api = AP_API_SANDBOX_OBSERVATIONS_PATH
    if not args.api_key:
        print ("Error: No API key provided (-k)")
        sys.exit(1)
    if args.ping_the_api:
        url = '%s%s%s' % (AP_API_ROOT_URL, api, 'environment')
        r = requests.get(url, headers=auth_headers(args.api_key))
        if args.verbose:
            print('GET %s' % url)
            print('HTTP Status code: %s' % (r.status_code))
            print('HTTP Response headers:')
            print(r.headers)
            print('HTTP Response body:')
        pprint.pprint(r.json())
    if args.get_observations:
        if not args.taxon_id:
            print("Error: No taxon id specified (--taxon-id)")
            sys.exit(2)
        url = '%s%s%s' % (AP_API_ROOT_URL,
                          api,
                          'sightings?taxonId=%s&dateFrom=%s&dateTo=%s&offset=%s&limit=%s' % (
                          args.taxon_id,
                          args.from_date,
                          args.to_date,
                          args.offset,
                          args.limit))
        r = requests.get(url, headers=auth_headers(args.api_key))
        if args.verbose:
            print('GET %s' % url)
            print('HTTP Status code: %s' % (r.status_code))
            print('HTTP Response headers:')
            print(r.headers)
            print('HTTP Response body:')
        pprint.pprint(r.json())
 


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

"""This is a CLI program that gets stuff from the Artdatabanken API:s and prints it to stdout."""

import sys
import argparse
import os
import os.path
from datetime import datetime
import dateutil.parser
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
ADB_COORDINATSYSTEM_WGS_84_ID = 10


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


def pretty_print_taxon(t):
    """Pretty print the taxon `t` to stdout."""
    print("%s (%s) taxon id: %s" % (t['swedishName'].capitalize(),
                                    t['scientificName'],
                                    t['taxonId']))
    print("%s (%s)" % (t['speciesData']['taxonRelatedInformation']['swedishPresence'],
                       t['speciesData']['taxonRelatedInformation']['immigrationHistory']))
    for item in t['speciesData']['redlistInfo']:
        print("%s:" % (item['period']['name']))
        print(" Kategori: %s" % (item['category']))
        print(" Text: %s" % (item['criterionText']))


def pretty_print_observation(o):
    """Pretty print the observation `o` to stdout."""
    fdate = dateutil.parser.parse(o['startDate'])
    edate = dateutil.parser.parse(o['endDate'])
    if fdate != edate:
        if fdate.hour != 0 and fdate.minute != 0 and edate.hour !=0 and edate.minute != 0:
            print("%s %s-%s" % ('{:%Y-%m-%d}'.format(fdate), '{:%H:%M}'.format(fdate), '{:%H:%M}'.format(edate)))
        else:
            print("%s" % ('{:%Y-%m-%d}'.format(fdate)))
    else:
        if fdate.hour != 0 and fdate.minute != 0:
            print("%s" % ('{:%Y-%m-%d %H:%M}'.format(fdate)))
        else:
            print("%s" % ('{:%Y-%m-%d}'.format(fdate)))
    print(" Upptäcksmetod: %s" % (o['discoveryMethod']))
    print(" Rapportör: %s" % (o['owner']))
    print(" Observatörer: %s" % (o['sightingObservers']))
    print(" Var: %s" % (o['site']['presentationName']))
    if o['publicComment']:
        s = o['publicComment'].strip()
    else:
        s = ""
    print(" Kommentar: %s" % (s))
    # Get WGS 84 coordinates so we can create URL:s for Google Maps and Open Street Map
    for c in o['site']['coordinates']:
        if c['coordinateSystemId'] == ADB_COORDINATSYSTEM_WGS_84_ID:
            easting = c['easting']
            northing = c['northing']
    gm_url = "https://www.google.com/maps/search/?api=1&query=%s,%s" % (northing, easting)
    osm_url = "https://www.openstreetmap.org/?mlat=%s&mlon=%s" % (northing, easting)
    print(" Google Maps location: %s" % (gm_url))
    print(" Open Street Maps location: %s" % (osm_url))
#    print(" Google Maps location: %s" % ("https://www.google.com/maps/@?api=1&map_action=map&center=56.711061,16.3535513&zoom=12&basemap=terrain"))
#    print(" Open Street Maps location: %s" % ("https://www.openstreetmap.org/?mlat=-38.3653&mlon=144.9069#map=9/-38.3653/144.9069"))


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
    parser.add_argument('--pretty-print', action='store_true', default=False,
                        help="Pretty print all info.")
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
        if args.pretty_print:
            for observation in reversed(r.json()['data']):
                pretty_print_observation(observation)
            fdate = dateutil.parser.parse(r.json()['data'][0]['startDate'])
            tdate = dateutil.parser.parse(r.json()['data'][-1]['startDate'])
            print("%s" % (50*'-'))
            print("%d observations (of total %s) shown of %s between %s and %s" % (len(r.json()['data']),
                                                                                   r.json()['pager']['totalCount'],
                                                                                   args.taxon_name,
                                                                                   '{:%Y-%m-%d}'.format(fdate),
                                                                                   '{:%Y-%m-%d}'.format(tdate)))
        else:
            pprint.pprint(r.json())
        sys.exit(0)
    if args.taxon_id:
        t = get_taxon_by_id(args, species_url, args.taxon_id)
        if t:
            if args.pretty_print:
                pretty_print_taxon(t[0])
            else:
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
        if args.pretty_print:
            pretty_print_taxon (t[0])
        else:
            pprint.pprint(t)
        sys.exit(0)


if __name__ == '__main__':
    main()

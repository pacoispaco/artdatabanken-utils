#!/usr/bin/env python3

"""This is the new CLI program that gets stuff from the Artdatabanken Observations API and Species API and prints it to stdout."""

import sys
import argparse
import os
import os.path
from datetime import datetime
import dateutil.parser
import pprint
import artportalen

# Constants
DEFAULT_CONF_FILE_PATH = 'adb-get.conf'
DEFAULT_FROM_DATE_RFC3339 = '1900-01-01T00:00'
ADB_SPECIES_API_KEY_ENV_NAME = 'ADB_SPECIES_API_KEY'
ADB_OBSERVATIONS_API_KEY_ENV_NAME = 'ADB_OBSERVATIONS_API_KEY'
ADB_API_ROOT_URL = 'https://api.artdatabanken.se'
ADB_SPECIES_API_PATH = '/information/v1/speciesdataservice/v1/'
ADB_OBSERVATIONS_API_PATH = '/species-observation-system/v1/Observations/Search'
ADB_COORDINATSYSTEM_WGS_84_ID = 10
AVES_TAXON_ID = 4000104


def species_api_key():
    """Value of the Species API key environment variable if it is set, otherwise None."""
    if ADB_SPECIES_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_SPECIES_API_KEY_ENV_NAME]
    else:
        return None


def observations_api_key():
    """Value of the Species API key environment variable if it is set, otherwise None."""
    if ADB_OBSERVATIONS_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_OBSERVATIONS_API_KEY_ENV_NAME]
    else:
        return None


def pretty_print_taxon(t):
    """Pretty print the taxon 't' to stdout."""
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
    """Pretty print the observation 'o' to stdout."""
    fdate = dateutil.parser.parse(o['startDate'])
    edate = dateutil.parser.parse(o['endDate'])
    if fdate != edate:
        if fdate.hour != 0 and fdate.minute != 0 and edate.hour != 0 and edate.minute != 0:
            print("%s %s-%s" % ('{:%Y-%m-%d}'.format(fdate),
                                '{:%H:%M}'.format(fdate),
                                '{:%H:%M}'.format(edate)))
        else:
            print("%s" % ('{:%Y-%m-%d}'.format(fdate)))
    else:
        if fdate.hour != 0 and fdate.minute != 0:
            print("%s" % ('{:%Y-%m-%d %H:%M}'.format(fdate)))
        else:
            print("%s" % ('{:%Y-%m-%d}'.format(fdate)))
    if 'discoveryMethod' in o:
        print(" Upptäcksmetod: %s" % (o['discoveryMethod']))
    else:
        print(" Upptäcksmetod: %s" % ("<attributet saknas>"))
    print(" Rapportör: %s" % (o['owner']))
    print(" Observatörer: %s" % (o['sightingObservers']))
    print(" Var: %s" % (o['site']['presentationName']))
    if 'publicComment' in o:
        print(" Kommentar: %s " % (o['publicComment'].strip()))
    else:
        print(" Kommentar: %s" % ("<atributet saknas>"))
    # Get WGS 84 coordinates so we can create URL:s for Google Maps and Open Street Map
    for c in o['site']['coordinates']:
        if c['coordinateSystemId'] == ADB_COORDINATSYSTEM_WGS_84_ID:
            easting = c['easting']
            northing = c['northing']
    gm_url = "https://www.google.com/maps/search/?api=1&query=%s,%s" % (northing, easting)
    osm_url = "https://www.openstreetmap.org/?mlat=%s&mlon=%s" % (northing, easting)
    print(" Google Maps location: %s" % (gm_url))
    print(" Open Street Maps location: %s" % (osm_url))
#    print(" Google Maps location: %s" % ("https://www.google.com/maps/@?api=1&
# map_action=map&center=56.711061,16.3535513&zoom=12&basemap=terrain"))
#    print(" Open Street Maps location: %s" % ("https://www.openstreetmap.org/?
# mlat=-38.3653&mlon=144.9069#map=9/-38.3653/144.9069"))


def today_RFC3339():
    """Today as an RFC 3339 / ISO 8601 date and time string, in minute resolution."""
    today = datetime.now()
    return today.isoformat(timespec='minutes')


def main():
    desc = """CLI-program for getting stuff from the Artdatabanken API:s. Note that you must set the
two API keys as environment variables. Ie:
export ADB_SPECIES_API_KEY=<API-KEY>
export ADB_OBSERVATIONS_API_KEY=<API-KEY>"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False].")
    parser.add_argument('-c', '--conf-file-path', default=DEFAULT_CONF_FILE_PATH,
                        help="Configuration file path [%s]." % (DEFAULT_CONF_FILE_PATH))
    parser.add_argument('--taxon-id',
                        help="Artdatabanken's taxon id")
    parser.add_argument('--taxon-name',
                        help="Artdatabanken's taxon name in Swedish")
    parser.add_argument('--exact-match', action='store_true', default=False,
                        help="Do exact match on taxon name [False]")
    parser.add_argument('--print-full-taxon-info', action='store_true', default=False,
                        help="Print full info on every taxon [False]")
    parser.add_argument('--pretty-print', action='store_true', default=False,
                        help="Pretty print all info.")
    parser.add_argument('-V', '--get-api-versions', action='store_true', default=False,
                        help="Get API versions.")
    parser.add_argument('-g', '--get-observations', action='store_true', default=False,
                        help="Get observations [False]")
    parser.add_argument('-s', '--show-search-filter', action='store_true', default=False,
                        help="Show the search filter used [False]. Use with '-g'")
    parser.add_argument('-r', '--sort-reverse', action='store_true', default=False,
                        help="Sort observations in reverse order [False]")
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
    if not species_api_key():
        print("Error: Environment variable ADB_SPECIES_API_KEY not set.")
        sys.exit(1)
    if not observations_api_key():
        print("Error: Environment variable ADB_OBSERVATIONS_API_KEY not set.")
        sys.exit(1)
    sapi = artportalen.SpeciesAPI(species_api_key())
    oapi = artportalen.ObservationsAPI(observations_api_key())
    if args.get_api_versions:
        v = oapi.version(args.verbose)
        print("Observations API:")
        pprint.pprint(v)
        print("Species API: No API resource for version")
        sys.exit(0)
    if args.taxon_name and args.taxon_id:
        print("Error: Flags --taxon-name and --taxon-id cannot be used at the same time.")
        sys.exit(1)
    if args.taxon_name:
        taxa = sapi.taxa_by_name(args.taxon_name,
                                 exact_match=args.exact_match,
                                 verbose=args.verbose)
        if not taxa:
            errmsg = (f"No taxon/taxa with name '{args.taxon_name}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(4)
        if not args.get_observations:
            # Then we print info on the named taxon/taxa
            if args.print_full_taxon_info:
                for taxon in taxa:
                    taxon_data = sapi.taxon_by_id(taxon['taxonId'], verbose=args.verbose)
                    pprint.pprint(taxon_data)
            else:
                pprint.pprint(taxa)
            print(f"Number of taxa: {len(taxa)}")
    if args.taxon_id:
        taxon_data = sapi.taxon_by_id(args.taxon_id, verbose=args.verbose)
        if not taxon_data:
            errmsg = (f"No taxon with id '{args.taxon_id}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(5)
        if not args.get_observations:
            # Then we print info on the taxon
            pprint.pprint(taxon_data)
    if args.get_observations:
        result = None
        if args.taxon_name:
            taxa = sapi.taxa_by_name(args.taxon_name)
            if not taxa:
                errmsg = (f"Error: No taxon with name '{args.taxon_name}' found "
                          "in Artdatabankens Species API.")
                print(errmsg)
                sys.exit(3)
            else:
                taxon_id = taxa[0]["taxonId"]
        elif args.taxon_id:
            taxon = sapi.taxon_by_id(args.taxon_id)
            if not taxon:
                errmsg = (f"Error: No taxon with id '{args.taxon_id}' found "
                          "in Artdatabankens Species API.")
                print(errmsg)
                sys.exit(4)
            else:
                taxon_id = args.taxon_id
        sfilter = artportalen.SearchFilter()
        sfilter.set_geographics_areas(areas=[{"area_type": "Municipality", "featureId": "180"}])
        sfilter.set_verification_status()
        sfilter.set_output()
        sfilter.set_date(startDate=args.from_date,
                         endDate=args.to_date,
                         dateFilterType="OverlappingStartDateAndEndDate",
                         timeRanges=[])
        sfilter.set_modified_date()
        sfilter.set_dataProvider()
        if args.taxon_name or args.taxon_id:
            sfilter.set_taxon(ids=[taxon_id])
        result = oapi.observations(sfilter,
                                   skip=args.offset,
                                   take=args.limit,
                                   sort_descending=not args.sort_reverse)
        pprint.pprint(result)
        if args.show_search_filter:
            print("==============")
            print("Search filter:")
            pprint.pprint(sfilter.filter)
        sys.exit(0)


if __name__ == '__main__':
    main()

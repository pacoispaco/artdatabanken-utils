# Module for accessing Artdatabankens Species Observation System API, aka SOS API.
# For more information see:
#   https://api-portal.artdatabanken.se/Products/sos
# You need an API key to access that API. For information on creating an account and getting
# an API key see:
#   https://api-portal.artdatabanken.se/
# Since the API is a very non REST-ful API there is a lot of out of band knowledge
# needed, in order to make valid calls. Many resources can be accessed with query parameters.
# Many are documented here:
#  https://github.com/biodiversitydata-se/SOS/blob/master/Docs/Vocabularies.md

import requests
import json
import pprint
import os

# Constants
API_NAME = 'Artdatabankens Species Observation System API'
API_INFO_URL = 'https://api-portal.artdatabanken.se/Products/sos'
API_ROOT_URL = 'https://api.artdatabanken.se'
API_ROOT_PATH = '/species-observation-system/v1/'
API_PING_RESOURCE = 'environment'
ADB_COORDINATSYSTEM_WGS_84_ID = 10


def auth_headers(api_key, auth_token=None):
    """Returns a dictionary of authentication headers for the SOS API."""
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


def print_http_response(r):
    """Print the HTTP resonse (from a requests.get call) to stdout."""
    print('HTTP Status code: %s' % (r.status_code))
    print('HTTP Response headers:')
    pprint.pprint(r.headers)
    print('HTTP Response body:')
    if r.json():
        pprint.pprint(r.json())


def ping_url():
    """Returns the URL used to ping the SOS API."""
    return "%s%s%s" % (API_ROOT_URL, API_ROOT_PATH, API_PING_RESOURCE)


def observations_search_filter():
    """A search filter for observations."""
    s = """{
            "dataProvider": {"ids": [1]},
            "date": {"startDate": "2022-02-12",
                     "endDate": "2022-02-12",
                     "dateFilterType": "OverlappingStartDateAndEndDate"},
            "geographics": {
                            "areas": [
                                      {
                                       "areaType": "Municipality",
                                       "featureId": "180"
                                      }
                                     ]
                           }
           }"""
    return s


class SOSAPI():
    """Represents the API."""

    def __init__(self, api_key):
        """Create a new API instance. A valid API-key 'api_key' must be provided."""
        self.api_key = api_key

    def ping(self, verbose=False):
        """Call the root resource of the API. Returns a requests response object."""
        r = requests.get(ping_url(), headers=auth_headers(self.api_key))
        if verbose:
            print("%s: %s" % (API_NAME, API_INFO_URL))
            print_http_response(url, r)
        return r

    def area_types(self):
        """Valid area types as documented here:
           https://github.com/biodiversitydata-se/SOS/blob/master/Docs/Vocabularies.md#areatype
           in the form of a dictionary indexed by area type id, where the entries are Swedish
           (sv-SE) and English (en-GB) names of the area types. Use the area id type when calling
           the API. By calling areas with type codes 1...1000 you get slightly different area types
           than documented above. The returned dictionary reflects all those area types returned by
           that API call."""
        return {1: {"sv-SE": "Kommun",
                    "en-GB": "Kommun"},
                12: {"sv-SE": "Sea",
                     "en-GB": "Sea"},
                13: {"sv-SE": "Landsdel",
                     "en-GB": "Landsdel"},
                15: {"sv-SE": "NatureType",
                     "en-GB": "NatureType"},
                16: {"sv-SE": "Provins",
                     "en-GB": "Provins"},
                17: {"sv-SE": "Ramsar",
                     "en-GB": "Ramsar"},
                18: {"sv-SE": "BirdValidationArea",
                     "en-GB": "BirdValidationArea"},
                19: {"sv-SE": "Socken",
                     "en-GB": "Socken"},
                20: {"sv-SE": "Spa",
                     "en-GB": "Spa"},
                21: {"sv-SE": "Län",
                     "en-GB": "Län"},
                22: {"sv-SE": "Skyddadnatur",
                     "en-GB": "Skyddadnatur"},
                24: {"sv-SE": "SwedishForestAgencyDistricts",
                     "en-GB": "SwedishForestAgencyDistricts"},
                26: {"sv-SE": "Sci",
                     "en-GB": "Sci"},
                27: {"sv-SE": "Vattenområde",
                     "en-GB": "Vattenområde"},
                29: {"sv-SE": "Atlas5x5",
                     "en-GB": "Atlas5x5"},
                30: {"sv-SE": "Atlas10x10",
                     "en-GB": "Atlas10x10"}}

    def areas(self, types=None, search_string=None, index=0, count=10, verbose=False):
        """Areas (regions)."""
        assert index >= 0
        assert count <= 1000
        url = "%s%s%s" % (API_ROOT_URL, API_ROOT_PATH, "Areas?")
        if types:
            url = url + "areaTypes=%s&" % (types)
        if search_string:
            url = url + "searchString=%s&" % (search_string)
        url = url + "skip=%d&take=%d" % (index, count)
        r = requests.get(url, headers=auth_headers(self.api_key))
        if verbose:
            print_http_response(url, r)
        return r

    def observations(self, search_filter, index=0, count=10, sort_by=None,
                     sort_order="Desc", lang="sv-SE", sensitive=False, verbose=False):
        """Observations matching 'search_filter'. Yeah, butt ugly."""
        assert index >= 0
        assert count <= 1000
        url = f"{API_ROOT_URL}{API_ROOT_PATH}Observations/search?skip={index}&take={count}&"
# url = "%s%s%s?skip=%d&take=%d&" % (API_ROOT_URL, API_ROOT_PATH,
# "Observations/Search", index, count)
        if sort_by:
            url = url + "sortBy=%s&" % (sort_by)
        url = url + "sortOrder=%s&translationCultureCode=%s&" % (sort_order, lang)
        if sensitive:
            url = url + "sensitiveObservations=true"
        else:
            url = url + "sensitiveObservations=false"
        headers = {**auth_headers(self.api_key), **{"Content-Type": "application/json"}}
        print(headers)
        r = requests.post(url,
                          data=search_filter,
                          headers=headers)
        if verbose:
            print_http_response(url, r)
        return r

    def observation(self, observation_id, output_field_set="All properties", lang="sv-SE",
                    sensitive=False, verbose=False):
        """Observation with the given 'observation_id'."""
        url = "%s%s%s%d?" % (API_ROOT_URL, API_ROOT_PATH, "Observations/", observation_id, )
        url = url + "outputFieldSet=%s&translationCultureCode=%si&" % (output_field_set, lang)
        if sensitive:
            url = url + "sensitiveObservations=true"
        else:
            url = url + "sensitiveObservations=false"
        r = requests.get(url, headers=auth_headers(self.api_key))
        if verbose:
            print_http_response(url, r)
        return r

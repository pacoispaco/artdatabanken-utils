#!/usr/bin/env python

"""
Python module for interacting with Artportalens API. This is the new implementation.
"""

import requests
import pprint
import json
from datetime import datetime

# Constants
DEFAULT_FROM_DATE_RFC3339 = '1900-01-01T00:00'
API_ROOT_URL = 'https://api.artdatabanken.se'
API_COORDINATSYSTEM_WGS_84_ID = 10
API_AVES_TAXON_ID = 4000104

EXAMPLE_SPECIES = "Tajgasångare"
EXAMPLE_TAXON_ID = 205835  # Id för Tajgasångare
EXAMPLE_SEARCH_FILTER_STR = """{
    "dataProvider": {
        "ids": []
    },
    "dataStewardship": {
        "datasetIdentifiers": []
    },
    "date": {
        "startDate": "2025-04-18",
        "endDate": "2025-04-18",
        "dateFilterType": "OverlappingStartDateAndEndDate",
        "timeRanges": []
    },
    "geographics": {
        "areas": [{
            "areaType": "Municipality",
            "featureId": "180"
        }],
    },
    "modifiedDate": {
        "from": null,
        "to": null
    },
    "taxon": {
        "includeUnderlyingTaxa": true,
        "ids": [4000104],
        "taxonListIds": [],
        "redListCategories": [],
        "taxonCategories": [],
        "taxonListOperator": "Merge"
    },
    "verificationStatus": "BothVerifiedAndNotVerified",
    "output": {
        "fieldSet": "Minimum",
        "fields": []
    }
}"""


class Taxon:

    def __init__(self):
        self.id = None
        self.name = None


class Observation:

    def __init__(self):
        self.id = None


class Person:

    def __init__(self):
        self.id = None
        self.user_name = None
        self.full_name = None


def auth_headers(api_key, auth_token=None):
    """Dictionary of authentication headers for API requests."""
    h = {'Ocp-Apim-Subscription-Key': api_key}
    if auth_token:
        h['Authorization'] = 'Bearer {%s}' % (auth_token)
    return h


def print_http_response(r):
    """Print the HTTP resonse (from a requests.get call) to stdout."""
    print('HTTP Status code: %s' % (r.status_code))
    print('HTTP Response headers:')
    pprint.pprint(r.headers)
    print('HTTP Response body:')
    if r.headers["Content-Type"] == "application/json":
        pprint.pprint(r.json())
    else:  # get the body but assume it can be decoded as a string
        pprint.pprint(r.content.decode())


class SpeciesAPI:
    """Handles requests to Artportalens Artfakta - Species information API."""

    def __init__(self, api_key: str):
        """Initialization. The client is responsible for managing secrets."""
        self.key = api_key
        self.url = API_ROOT_URL + "/information/v1/speciesdataservice/v1/"
        self.search_url = self.url + "speciesdata"
        self.headers = auth_headers(self.key)

    def taxa_by_name(self, name, exact_match=True, verbose=False):
        """Returns list of all taxa that match the name."""
        url = self.search_url + f"/search?searchString={name}"
        r = requests.get(url, headers=self.headers)
        if verbose:
            print('GET %s' % url)
            print_http_response(r)
        if r.status_code == 200:
            for d in r.json():
                if exact_match:
                    if d['swedishName'] == name.lower():
                        return [d]
                else:
                    return r.json()
        else:
            if verbose:
                print("Something went wrong in the API request.")
        return None

    def taxon_by_id(self, id, verbose=False):
        """Returns the taxon with the given id."""
        url = self.search_url + f"?taxa={id}"
        r = requests.get(url, headers=self.headers)
        if verbose:
            print('GET %s' % url)
            print_http_response(r)
        if r.json() == []:
            return None
        else:
            return r.json()


class SearchFilter:
    """Represents the search filter object that is used to search in the ObservationsAPI. An
       actual search filter must be sent as a literal JSON object in the body of the POST request
       to the ObservationsAPI."""

    def __init__(self):
        """Intitialization."""
        current_date = datetime.today().strftime('%Y-%m-%d')
        self.filter = {"dataProvider": {"ids": [1]},
                       "dataStewardship": {"datasetIdentifiers": []},
                       "date": {"startDate": current_date,
                                "endDate": current_date,
                                "dateFilterType": "OverlappingStartDateAndEndDate",
                                "timeRanges": []}
                       }

    def json_string(self):
        """Returns a JSON string representation of this filter."""
        return json.dumps(self.filter)

    def set_dataProvider(self, ids: list[str] = []):
        """Set the data providers by providing a list of id:s.
           Use `ObservationsAPI.data_providers()` to find out valid data providers."""
        self.filter["dataProvider"] = {"ids": ids}

    def set_dataStewardship(self, datasetIdentifiers: list[str] = []):
        """Set the dataStewardship by providing a list of id:s."""
        self.filter["dataStewardship"] = {"datasetIdentifiers": datasetIdentifiers}

    def set_date(self,
                 startDate: str = None,
                 endDate: str = None,
                 dateFilterType: str = None,
                 timeRanges: list[str] = None):
        """Set the start and end dates, date filter type and time range where time range can be
           one of "Morning", "Forenoon", "Afternoon", "Evening" or Night."""
        self.filter["date"] = {"startDate": startDate,
                               "endDate": endDate,
                               "dateFilterType": dateFilterType,
                               "timeRanges": timeRanges}

    def set_modified_date(self, from_date: str = None, to_date: str = None):
        """Set the modified date criteria."""
        self.filter["modifiedDate"] = {"from": from_date,
                                       "to": to_date}

    def set_geographics_areas(self, areas: list[dict]):
        """Set the geographics of the search filter by specifying one or more defined and
           identified geographical areas.
           Every dict must have this structure:
           {"areaType": str,
            "featureId": str}
           where "areaType" can be one of; "Municipality", "Community", "Sea", "CountryRegion",
           "NatureType", "Province", "Ramsar", "BirdValidationArea", "Parish", "Spa", "County",
           "ProtectedNature", "SwedishForestAgencyDistricts", "Sci", "WaterArea", "Atlas5x5",
           "Atlas10x10", "SfvDistricts" or "Campus" and "featureId" is an id of an instance of
           those areaType:s."""
        self.filter["geographics"] = {"areas": areas}

    def set_geographics_geometries(self,
                                   geometries: list[str],
                                   considerDisturbanceRadius: bool = False,
                                   considerObservationAccuracy: bool = False,
                                   maxDistanceFromPoint: float = None):
        """Set the geographics of the search filter by specifying point or polygon. We assume
           in WGS84 coordinates and formatted in some sensible string format well just guess.
           In the API documentation at https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=GeographicsFilterDtothey call theylist the type as being IGeoShape and
           elsewhere in the documentation they say they use ElasticSearch for the search
           features of the API, so see:
           https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/geo-shape"""
        self.filter["geographics"] = {"geometries": geometries}

    def set_geographics_bounding_box(self,
                                     bottomRight_latitude: float,
                                     bottomRight_longitude: float,
                                     topLeft_latitude: float,
                                     topLeft_longitude: float):
        """Set the geographics of the search filter by specifying a bounding box.
           We assume latitude and logitude values are WGS84.
           see: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=LatLonBoundingBoxDto"""
        bb = {"boundingBox": {"bottomRight": {"latitude": bottomRight_latitude,
                                              "longitude": bottomRight_longitude},
                              "topLeft": {"latitude": topLeft_latitude,
                                          "longitude": topLeft_longitude}}}
        self.filter["geographics"] = bb

    def set_taxon(self, ids: list[str],
                  taxonListIds: list[str] = None,
                  includeUnderlyingTaxa: bool = True,
                  redListCategories: list[str] = None,
                  taxonCategories: list[str] = None,
                  taxonListOperator: str = "Merge"):
        """Set the taxon to search for. redListCategories can be one of "DD", "EX", "RE", "CR",
           "EN", "VU", "NT", "LC", "NA" or "NE". taxonListOperator can be one of "Merge" ord
           "Filter".
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&definition=TaxonFilterDto"""
        self.filter["taxon"] = {"includeUnderlyingTaxa": includeUnderlyingTaxa,
                                "ids": ids,
                                "taxonListIds": taxonListIds,
                                "redListCategories": redListCategories,
                                "taxonCategories": taxonCategories,
                                "taxonListOperator": taxonListOperator}

    def set_verification_status(self, verificationStatus: str = "BothVerifiedAndNotVerified"):
        """Set the verification status of the search filter. It can be one of "Verified",
           "NotVerified" or "BothVerifiedAndNotVerified".
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=StatusVerificationDto"""
        self.filter["verificationStatus"] = verificationStatus

    def set_output(self, fieldSet: str = "Minimum", fields: list[str] = []):
        """Set the output scope of the search filter.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&definition=OutputFilterDto"""
        self.filter["output"] = {"fieldSet": fieldSet,
                                 "fields": fields}


class ObservationsAPI:
    """Handles requests to Artportalens Species Observations Service API."""

    # See the Observation object in the API for alternative attributes to sort by.
    DEFAULT_SORT_BY_ATTRIBUTE_FOR_OBSERVATIONS = 'event.startDate'

    def __init__(self, api_key: str):
        """Initialization. The client is responsible for managing secrets."""
        self.key = api_key
        self.url = API_ROOT_URL + "/species-observation-system/v1/"
        self.search_url = self.url + "Observations/Search"
        self.headers = auth_headers(self.key)

    def last_response(self):
        """Returns the last response (a requests response object). Use this to check any problems
           in the last API request. You can use the attributes "status_code" and "content" to find
           out more. See: https://requests.readthedocs.io/en/latest/api/#requests.Response"""
        return self.last_response

    def version(self, verbose=False):
        """Returns version of the API. This can be used to ping the API.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=ApiInfo_GetApiInfo"""
        url = self.url + "api/ApiInfo"
        r = requests.get(url, headers=self.headers)
        if verbose:
            print('GET %s' % url)
            print_http_response(r)
        return r.json()

    def data_providers(self, verbose=False):
        """Returns a list of data providers that have observations in the API.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=DataProviders_GetDataProviders"""
        url = self.url + "/DataProviders"
        r = requests.get(url, headers=self.headers)
        if verbose:
            print('GET %s' % url)
            print_http_response(r)
        return r.json()

    def observations_test(self, verbose=False):
        """Returns the observations based on a hard coded search filter."""
        url = self.search_url
        params = {"skip": 0,
                  "take": 200,
                  "sortBy": "event.Startdate",
                  "sortOrder": "Desc"}
        headers = self.headers | {"Content-Type": "application/json"}
        search_filter = EXAMPLE_SEARCH_FILTER_STR
        if verbose:
            print(f"HTTP request: POST {url}")
            print(f"HTTP headers: {headers}")
            print(f"HTTP body: {search_filter}")
        r = requests.post(url, params=params, headers=headers, data=search_filter)
        self.last_response = r
        if r.ok:
            self.last_response = r
            if verbose:
                print_http_response(r)
            return r.json()
        else:
            return None

    def observations(self, search_filter: SearchFilter,
                     skip: int = 0,
                     take: int = 100,  # Maximum is 1000
                     sortBy: str = DEFAULT_SORT_BY_ATTRIBUTE_FOR_OBSERVATIONS,
                     sort_descending: bool = True,
                     validateSearchFilter: bool = False,  # Validation will be done.
                     translationCultureCode: str = None,  # "sv-SE" or "en-GB"
                     sensitiveObservations: bool = False,  # If true, only sensitive observations
                                                           # will be searched.
                     verbose=False):
        """Returns `take` observations starting at `skip` + 1 according to the criteria in
           the `search_filter` and the other request parameters.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch"""
        if sort_descending:
            sortOrder = 'Desc'
        else:
            sortOrder = 'Asc'
        url = self.search_url
        params = {"skip": skip,
                  "take": take,
                  "sortBy": sortBy,
                  "sortOrder": sortOrder,
                  "validateSearchFilter": validateSearchFilter,
                  "translationCultureCode": translationCultureCode}
        headers = self.headers | {"Content-Type": "application/json"}
        if verbose:
            print(f"HTTP request: POST {url}")
            print(f"HTTP headers: {headers}")
            print(f"HTTP body: {search_filter.json_string()}")
        r = requests.post(url, params=params, headers=headers, data=search_filter.json_string())
        self.last_response = r
        if r.ok:
            if verbose:
                print_http_response(r)
            return r.json()
        else:
            return None

    def observations_by_georegion(self, from_date: str, to_date: str,
                                  region_type: str, region_name: str):
        """Returns the observations in a named geographical region."""

    def observations_by_geopolygon(self, from_date: str, to_date: str, polygon: list):
        """Returns the observations within a specified geographical polygon."""

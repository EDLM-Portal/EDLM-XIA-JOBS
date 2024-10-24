import hashlib
import json
import logging
from datetime import datetime

import html2text
import pandas as pd
import requests
from bs4 import BeautifulSoup

from core.management.utils.eccr_client import get_eccr_UUID
from core.management.utils.xia_internal import (dict_flatten, get_key_dict,
                                                traverse_dict_with_key_list)
# from core.serializers import MetadataLedgerSerializer

logger = logging.getLogger('dict_config_logger')


# class TokenAuth(AuthBase):
#     """Attaches HTTP Authentication Header to the given Request object."""

#     def __call__(self, r, token_name='Authorization-Key'):
#         # modify and return the request

#         r.headers[token_name] = get_P1PS_team_token()
#         return r


def get_xsr_api_endpoint(xsr_obj, page, endpoint):
    """Setting API endpoint from XIA and XIS communication """
    logger.debug("Retrieve xsr_api_endpoint from XSR configuration")
    xsr_endpoint = xsr_obj.xsr_api_endpoint + endpoint
    return xsr_endpoint, xsr_obj.token


def get_xsr_api_response(xsr_obj, page, endpoint):
    """Function to get api response from xsr endpoint"""
    # url of rss feed

    xsr_data, token = get_xsr_api_endpoint(xsr_obj, page, endpoint)

    url = xsr_data
    headers = {"Authorization-Key": token}

    # creating HTTP response object from given url
    try:
        resp = requests.get(url, verify=False, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.error(e)
        raise SystemExit('Exiting! Can not make connection with XSR.')

    return resp


# Function to convert
def listToString(s):
    # initialize an empty string
    str1 = ", "
    # return string
    return (str1.join(s))


def custom_Jobs_edits(source_data):
    """Function to perform custom edits to USA jobs data"""
    for data in source_data:
        for key in data["MatchedObjectDescriptor"]:
            if isinstance(data["MatchedObjectDescriptor"][key], list):
                data_list = []
                for each_instance in data["MatchedObjectDescriptor"][key]:
                    if isinstance(each_instance, dict):
                        value = json.dumps(each_instance)
                        data_list.append(value)
                data["MatchedObjectDescriptor"][key] = data_list
                data["MatchedObjectDescriptor"][key] =\
                    listToString(data["MatchedObjectDescriptor"][key])


def extract_source(xsr_obj):
    """function to parse xml xsr data and convert to dictionary"""

    page = 1

    resp = get_xsr_api_response(xsr_obj, page, "/api/codelist/cyberworkroles")

    cwr_dict = json.loads(resp.text)

    cwr_code = cwr_dict["CodeList"][0]["ValidValue"]
    cwr_list = []

    for data in cwr_code:
        cwr_list.append(data["Code"])

    cwr_len = len(cwr_list)
    source_df_list = []

    for code in cwr_list:
        endpoint = '/api/Search?cwr=' + code
        resp_code = get_xsr_api_response(xsr_obj, page, endpoint)

        if resp.status_code == 200:
            source_data_dict = json.loads(resp_code.text)

            logger.info("Retrieving data from source page " + str(page))

            source_data = source_data_dict["SearchResult"]["SearchResultItems"]

            source_df = pd.DataFrame(source_data)

            eccr_uuid = get_eccr_UUID(code)
            source_df["code"] = code
            if eccr_uuid:
                source_df["eccr_uuid"] = str(eccr_uuid)
            else:
                source_df["eccr_uuid"] = eccr_uuid

            logger.info("Retrieving data from source page " + str(page))
            source_df_list.append(source_df)

            if page >= cwr_len:
                source_df_final = pd.concat(source_df_list).reset_index(
                    drop=True)
                logger.info("Completed retrieving data from source")
                return source_df_final
            page = page + 1


def read_source_file(xsr_obj):
    """sending source data in dataframe format"""
    logger.info("Retrieving data from XSR")
    # load rss from web to convert to xml
    xsr_items = extract_source(xsr_obj)
    # convert xsr dictionary list to Dataframe
    source_df = pd.DataFrame(xsr_items)
    logger.info("Changing null values to None for source dataframe")
    std_source_df = source_df.where(pd.notnull(source_df),
                                    None)
    return [std_source_df]


def get_source_metadata_key_value(data_dict):
    """Function to create key value for source metadata """
    # field names depend on source data and SOURCESYSTEM is system generated
    field = ['MatchedObjectDescriptor.PositionID', 'code', 'SOURCESYSTEM']
    field_values = []

    data_flattened = dict_flatten(data_dict, [])

    for item in field:
        if not data_flattened.get(item):
            logger.error('Field name ' + item + ' is missing for '
                                                'key creation')
            return None
        field_values.append(data_flattened.get(item))

    # Key value creation for source metadata
    key_value = '_'.join(field_values)

    # Key value hash creation for source metadata
    key_value_hash = hashlib.sha512(key_value.encode('utf-8')).hexdigest()

    # Key dictionary creation for source metadata
    key = get_key_dict(key_value, key_value_hash)

    return key


def convert_int_to_date(element, target_data_dict):
    """Convert integer date to date time"""
    key_list = element.split(".")
    check_key_dict = target_data_dict
    check_key_dict = traverse_dict_with_key_list(check_key_dict, key_list)
    if check_key_dict:
        if key_list[-1] in check_key_dict:
            if isinstance(check_key_dict[key_list[-1]], int):
                check_key_dict[key_list[-1]] = datetime. \
                    fromtimestamp(check_key_dict[key_list[-1]])


def find_dates(data_dict):
    """Function to convert integer value to date value """

    data_flattened = dict_flatten(data_dict, [])

    for element in data_flattened.keys():
        element_lower = element.lower()
        if (element_lower.find("date") != -1 or element_lower.find(
                "time")) != -1:
            convert_int_to_date(element, data_dict)
    return data_dict


def convert_html(element, target_data_dict):
    """Convert HTML to text data"""
    key_list = element.split(".")
    check_key_dict = target_data_dict
    check_key_dict = traverse_dict_with_key_list(check_key_dict, key_list)
    if check_key_dict:
        if key_list[-1] in check_key_dict:
            check_key_dict[key_list[-1]] = \
                html2text.html2text(check_key_dict[key_list[-1]])


def find_html(data_dict):
    """Function to convert HTML value to text"""
    data_flattened = dict_flatten(data_dict, [])

    for element in data_flattened.keys():
        if data_flattened[element]:
            if bool(BeautifulSoup(str(data_flattened[element]),
                                  "html.parser").find()):
                convert_html(element, data_dict)
    return data_dict

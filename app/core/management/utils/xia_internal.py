import datetime
import hashlib
import logging
# from distutils.util import strtobool
from str2bool import str2bool

from core.models import XIAConfiguration
from dateutil.parser import parse

logger = logging.getLogger('dict_config_logger')


def get_publisher_detail():
    """Retrieve publisher from XIA configuration """
    logger.debug("Retrieve publisher from XIA configuration")
    xia_data = XIAConfiguration.objects.first()
    publisher = xia_data.publisher
    return publisher


def traverse_dict_with_key_list(check_key_dict, key_list):
    """Function to traverse through dict with a key list"""
    for key in key_list[:-1]:
        if key in check_key_dict:
            check_key_dict = check_key_dict[key]
        else:
            check_key_dict = None
            logger.error("Path to traverse dictionary is "
                         "incorrect/ does not exist")
            return check_key_dict
    return check_key_dict


def get_key_dict(key_value, key_value_hash):
    """Creating key dictionary with all corresponding key values"""
    key = {'key_value': key_value, 'key_value_hash': key_value_hash}
    return key


def get_target_metadata_key_value(data_dict):
    """Function to create key value for target metadata """
    field = {
        "Job_Vacancy_Data": [
            "JobPostingID",
            "code",
            "ProviderName"
        ]
    }

    field_values = []

    for item_section in field:
        for item_name in field[item_section]:
            if not data_dict[item_section].get(item_name):
                logger.info('Field name ' + item_name + ' is missing for '
                                                        'key creation')
            field_values.append(data_dict[item_section].get(item_name))

    # Key value creation for source metadata
    key_value = '_'.join(field_values)

    # Key value hash creation for source metadata
    key_value_hash = hashlib.sha512(key_value.encode('utf-8')).hexdigest()

    # Key dictionary creation for source metadata
    key = get_key_dict(key_value, key_value_hash)

    return key


def required_recommended_logs(id_num, category, field):
    """logs the missing required and recommended """

    # Use a const to satisfy code smells
    record_str = "Record "

    # Logs the missing required columns
    if category == 'Required':
        logger.error(
            record_str + str(
                id_num) + " does not have all " + category +
            " fields."
            + field + " field is empty")

    # Logs the missing recommended columns
    if category == 'Recommended':
        logger.warning(
            record_str + str(
                id_num) + " does not have all " + category +
            " fields."
            + field + " field is empty")

    # Logs the inaccurate datatype columns
    if category == 'datatype':
        logger.warning(
            record_str + str(
                id_num) + " does not have the expected " + category +
            " for the field " + field)


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    if isinstance(string, str):
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False
    else:
        return False


def dict_flatten(data_dict, required_column_list):
    """Function to flatten/normalize  data dictionary"""

    # assign flattened json object to variable
    flatten_dict = {}

    # Check every key elements value in data
    for element in data_dict:
        # If Json Field value is a Nested Json
        if isinstance(data_dict[element], dict):
            flatten_dict_object(data_dict[element],
                                element, flatten_dict, required_column_list)
        # If Json Field value is a string
        else:
            update_flattened_object(data_dict[element],
                                    element, flatten_dict)

    # Return the flattened json object
    return flatten_dict


def flatten_dict_object(dict_obj, prefix, flatten_dict, required_column_list):
    """function to flatten dictionary object"""
    for element in dict_obj:
        if isinstance(dict_obj[element], dict):
            flatten_dict_object(dict_obj[element], prefix + "." +
                                element, flatten_dict, required_column_list)
        else:
            update_flattened_object(dict_obj[element], prefix + "." +
                                    element, flatten_dict)


def update_flattened_object(str_obj, prefix, flatten_dict):
    """function to update flattened object to dict variable"""

    if isinstance(str_obj, str):
        flatten_dict.update({prefix: str_obj})
    else:
        flatten_dict[prefix] = str(str_obj)


def convert_date_to_isoformat(date):
    """function to convert date to ISO format"""
    if isinstance(date, datetime.datetime):
        date = date.isoformat()
    return date


def type_cast_overwritten_values(field_type, field_value):
    """function to check type of overwritten value and convert it into
    required format"""

    value = field_value
    if field_value:
        if field_type == "int":
            try:
                value = int(field_value)
            except Exception as e: # pylint: disable=broad-except
                logger.error(e)

        elif field_type == "bool":
            try:
                value = str2bool(field_value)
            except Exception as e: # pylint: disable=broad-except
                logger.error(e)

        elif field_type == "datetime":
            try:
                is_date(field_value)
            except Exception as e: # pylint: disable=broad-except
                logger.error(e)

    else:
        return None

    return value

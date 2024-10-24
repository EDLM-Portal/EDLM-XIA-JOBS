import hashlib
import logging
from datetime import datetime
from unittest.mock import patch

from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xia_internal import (dict_flatten,
                                                flatten_dict_object,
                                                flatten_list_object,
                                                get_key_dict,
                                                get_publisher_detail,
                                                get_target_metadata_key_value,
                                                is_date,
                                                # replace_field_on_target_schema,
                                                type_cast_overwritten_values,
                                                update_flattened_object)
from core.management.utils.xis_client import get_xis_metadata_api_endpoint
from core.management.utils.xsr_client import (convert_html,
                                              convert_int_to_date, find_dates,
                                              find_html,
                                              get_source_metadata_key_value,
                                              get_xsr_api_endpoint,
                                              get_xsr_api_response,
                                              listToString, read_source_file)
from core.management.utils.xss_client import (
    get_data_types_for_validation, get_required_fields_for_validation,
    get_source_validation_schema, get_target_metadata_for_transformation,
    get_target_validation_schema, read_json_data, xss_get)
from core.models import XIAConfiguration, XISConfiguration

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit1')
@ddt
class UtilsTests(TestSetUp):
    """Unit Test cases for utils """

    # Test cases for XSR_CLIENT
    def test_get_xsr_api_endpoint(self):
        """Test to check if API endpoint is present"""
        api_end, tk = get_xsr_api_endpoint(self.xsrConfig)
        self.assertEqual(self.xsr_api_endpoint_url, api_end)
        self.assertEqual(self.token, tk)

    def test_get_xsr_api_response(self):
        """Test to Function to get api response from xsr endpoint"""
        with patch('core.management.utils.xsr_client.get_xsr_api_endpoint') \
                as xsr_ep, patch('requests.get') as response_obj:
            xsr_ep.return_value = self.xsr_api_endpoint_url, self.token
            response_obj.return_value = response_obj

            result_xsr_api_response = get_xsr_api_response(self.xsrConfig)
            self.assertTrue(result_xsr_api_response)

    @patch('core.management.utils.xsr_client.extract_source',
           return_value=dict({1: {'a': 'b'}}))
    def test_read_source_file(self, extract):
        """test to check if data is present for extraction """

        result_data = read_source_file(self.xsrConfig)
        self.assertIsInstance(result_data, list)

    def test_listToString(self):
        converted_string = listToString('[1, 2, 3, 4]')

        self.assertTrue(isinstance(converted_string, str))

    def test_find_html(self):

        html_dict = {'html_code': '<h1>This is heading 1</h1>'}
        converted_html_dict = find_html(html_dict)
        self.assertTrue(isinstance(converted_html_dict['html_code'], str))

    def test_find_dates(self):

        date_int = {'date': 1718050925}
        date_dict = find_dates(date_int)
        self.assertTrue(isinstance(date_dict['date'], datetime))

    def test_convert_html(self):

        html_dict = {'html_code': '<h1>This is heading 1</h1>'}
        convert_html('html_code', html_dict)
        self.assertTrue(isinstance(html_dict['html_code'], str))

    def test_convert_int_to_date(self):

        date_int = {'date': 1718050925}
        convert_int_to_date('date', date_int)
        self.assertTrue(isinstance(date_int['date'], datetime))

    @patch('core.management.utils.xsr_client.get_xsr_api_endpoint',
           return_value=('xsr_url', 'token'))
    def test_custom_moodle_fields(self, ret):

        Val = custom_moodle_fields([self.source_metadata], self.xsrConfig) # type: ignore
        self.assertFalse(Val)

    @patch('core.management.utils.xsr_client.get_xsr_api_endpoint',
           return_value=('xsr_url', 'token'))
    def test_custom_moodle_fields_true(self, ret):

        source_dict = self.source_metadata
        source_dict.update({"categoryname": "ecc approved"})

        Val = custom_moodle_fields([source_dict], self.xsrConfig) # type: ignore
        self.assertTrue(Val)

    @data(('key_field1', 'key_field2'), ('key_field11', 'key_field22'))
    @unpack
    def test_get_source_metadata_key_value(self, first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'idnumber': first_value,
            'SOURCESYSTEM': second_value
        }

        expected_key = first_value + '_' + second_value
        expected_key_hash = hashlib.sha512(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_source_metadata_key_value(test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)

    @data(('key_field1', ''))
    @unpack
    def test_get_source_metadata_key_value_fail(self,
                                                first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'idnumber': first_value,
            'SOURCESYSTEM': second_value
        }

        result_key_dict = get_source_metadata_key_value(test_dict)

        self.assertEqual(result_key_dict, None)

    def test_get_publisher_detail(self):
        """Test to retrieve publisher from XIA configuration"""
        with patch('core.management.utils.xia_internal'
                   '.XIAConfiguration.objects') as xiaCfg:
            xiaConfig = XIAConfiguration(publisher='AGENT')
            xiaCfg.first.return_value = xiaConfig
            return_from_function = get_publisher_detail()
            self.assertEqual(xiaConfig.publisher, return_from_function)

    @data(('test_key', 'test_key_hash'), ('test_key1', 'test_key_hash2'))
    @unpack
    def test_get_key_dict(self, first_value, second_value):
        """Test for key dictionary creation"""
        expected_result = {
            'key_value': first_value,
            'key_value_hash': second_value
        }
        result = get_key_dict(first_value, second_value)
        self.assertEquals(result, expected_result)

    @data((1, False), ("1990-12-1", True), ("Monday at 12:01am", True))
    @unpack
    def test_is_date(self, value_to_be_tested, result):
        """tests whether the string can be interpreted as a date."""
        check = is_date(value_to_be_tested)
        self.assertEqual(check, result)

    @data(('key_field1', 'key_field2'), ('key_field11', 'key_field22'))
    @unpack
    def test_get_target_metadata_key_value(self, first_value, second_value):
        """Test key dictionary creation for target"""

        test_dict = {'Course': {
            'CourseCode': first_value,
            'CourseProviderName': second_value
        }}

        expected_key = first_value + '_' + second_value
        expected_key_hash = hashlib.sha512(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_target_metadata_key_value(test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)

    def test_dict_flatten(self):
        """Test function to navigate to value in source
        metadata to be validated"""
        test_data_dict = {"key1": "value1",
                          "key2": {"sub_key1": "sub_value1"},
                          "key3": [{"sub_key2": "sub_value2"},
                                   {"sub_key3": "sub_value3"}]}

        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

        return_value = dict_flatten(test_data_dict,
                                    self.test_required_column_names)
        self.assertTrue(return_value)

    @data(
        ([{'a.b': None, 'a.c': 'value2', 'd': None},
          {'a.b': 'value1', 'a.c': 'value2', 'd': None}]))
    def test_flatten_list_object_loop(self, value):
        """Test the looping od the function to flatten
        list object when the value is list"""
        prefix = 'a'
        flatten_dict = {}
        required_list = ['a.b', 'a.c', 'd']
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_'
                    'object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_'
                    'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.side_effect = flatten_dict = \
                {'a.b': None, 'a.c': 'value2'}

            flatten_list_object(value, prefix, flatten_dict, required_list)
            self.assertEqual(mock_flatten_dict.call_count, 2)

    @data(
        ([{'b': [None]}]))
    def test_flatten_list_object_multilevel(self, value):
        """Test the function to flatten list object
         when the value is list for multilevel lists"""
        prefix = 'a'
        flatten_dict = {}
        required_list = ['a.b', 'd']
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') \
                as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_'
                    'object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_'
                    'object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_update_flattened
            mock_flatten_dict.return_value = mock_flatten_list()
            mock_update_flattened.side_effect = flatten_dict = \
                {'a.b': None}

            flatten_list_object(value, prefix, flatten_dict, required_list)
            self.assertEqual(mock_flatten_list.call_count, 1)

    @data(([{'A': 'a'}]), ([{'B': 'b', 'C': 'c'}]))
    def test_flatten_list_object_list(self, value):
        """Test the function to flatten list object when the value is list"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data(([{'A': 'a'}]), ([{'B': 'b', 'C': 'c'}]))
    def test_flatten_list_object_dict(self, value):
        """Test the function to flatten list object when the value is dict"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data((['hello']), (['hi']))
    def test_flatten_list_object_str(self, value):
        """Test the function to flatten list object when the value is string"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None
            flatten_list_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_update_flattened.call_count, 1)

    @data(({'abc': {'A': 'a'}}), ({'xyz': {'B': 'b'}}))
    def test_flatten_dict_object_dict(self, value):
        """Test the function to flatten dictionary object when input value is
        a dict"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_dict.call_count, 1)

    @data(({'abc': [1, 2, 3]}), ({'xyz': [1, 2, 3, 4, 5]}))
    def test_flatten_dict_object_list(self, value):
        """Test the function to flatten dictionary object when input value is
        a list"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_flatten_list.call_count, 1)

    @data(({'abc': 'A'}), ({'xyz': 'B'}))
    def test_flatten_dict_object_str(self, value):
        """Test the function to flatten dictionary object when input value is
        a string"""
        prefix = 'test'
        flatten_dict = []
        with patch(
                'core.management.utils.xia_internal.'
                'flatten_list_object') as mock_flatten_list, \
                patch(
                    'core.management.utils.xia_internal.'
                    'flatten_dict_object') as mock_flatten_dict, \
                patch(
                    'core.management.utils.xia_internal.'
                    'update_flattened_object') as mock_update_flattened:
            mock_flatten_list.return_value = mock_flatten_list
            mock_flatten_list.return_value = None
            mock_flatten_dict.return_value = mock_flatten_dict
            mock_flatten_dict.return_value = None
            mock_update_flattened.return_value = mock_update_flattened
            mock_update_flattened.return_value = None

            flatten_dict_object(value, prefix, flatten_dict,
                                self.test_required_column_names)

            self.assertEqual(mock_update_flattened.call_count, 1)

    @data('', 'str1')
    def test_update_flattened_object(self, value):
        """Test the function which returns the source bucket name"""
        prefix = 'test'
        flatten_dict = {}
        update_flattened_object(value, prefix, flatten_dict)
        self.assertTrue(flatten_dict)

    @data(("int", '1234'), ("int", '-12'))
    @unpack
    def test_type_cast_overwritten_values(self, first_value, second_value):
        """Test the function to check type of overwritten value and convert it
        into required format"""
        field_type = first_value
        field_value = second_value
        values = type_cast_overwritten_values(field_type, field_value)
        self.assertIsInstance(values, int)

    @data(("int", ''))
    @unpack
    def test_type_cast_overwritten_values_None(self, first_value,
                                               second_value):
        """Test the function to check type of overwritten value and convert it
        into required format"""
        field_type = first_value
        field_value = second_value
        values = type_cast_overwritten_values(field_type, field_value)
        self.assertFalse(values)

    @data(("int", "test"))
    @unpack
    def test_type_cast_overwritten_values_false(self, first_value,
                                                second_value):
        """Test the function to check type of overwritten value and convert it
        into required format"""
        field_type = first_value
        field_value = second_value
        values = type_cast_overwritten_values(field_type, field_value)
        self.assertNotIsInstance(values, int)

    # Test cases for XIS_CLIENT

    def test_get_xis_metadata_api_endpoint(self):
        """Test to retrieve xis_metadata_api_endpoint from XIS configuration"""
        with patch('core.management.utils.xis_client'
                   '.XISConfiguration.objects') as xisCfg:
            xisConfig = XISConfiguration(
                xis_metadata_api_endpoint=self.xis_api_endpoint_url)
            xisCfg.first.return_value = xisConfig
            return_from_function = get_xis_metadata_api_endpoint()
            self.assertEqual(xisConfig.xis_metadata_api_endpoint,
                             return_from_function)

    def test_get_xis_supplemental_metadata_api_endpoint(self):
        """Test to retrieve xis_supplemental_api_endpoint from XIS
        configuration"""
        with patch('core.management.utils.xis_client'
                   '.XISConfiguration.objects') as xisCfg:
            xisConfig = XISConfiguration(
                xis_supplemental_api_endpoint=self.supplemental_api_endpoint)
            xisCfg.first.return_value = xisConfig
            return_from_function = get_xis_supplemental_metadata_api_endpoint() # type: ignore
            self.assertEqual(xisConfig.xis_supplemental_api_endpoint,
                             return_from_function)

    # Test cases for XSS_CLIENT

    def test_get_source_validation_schema(self):
        """Test to retrieve source_metadata_schema from XIA configuration"""
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xdsCfg, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                source_metadata_schema='AGENT_source_validate_schema.json')
            xdsCfg.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.schema_data_dict
            return_from_function = get_source_validation_schema()
            self.assertEqual(read_obj.return_value,
                             return_from_function)

    def test_get_data_types_for_validation(self):
        """Creating list of fields with the expected datatype objects"""

        converted_dict = \
            get_data_types_for_validation(self.datatype_list_as_string)
        self.assertEqual(converted_dict, self.datatype_list_as_object)

    def test_get_required_fields_for_validation(self):
        """Test for Creating list of fields which are Required """

        required_column_name, recommended_column_name = \
            get_required_fields_for_validation(self.schema_data_dict)

        self.assertTrue(required_column_name)
        self.assertTrue(recommended_column_name)

    def test_get_target_validation_schema(self):
        """Test to retrieve target_metadata_schema from XIA configuration"""
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xiaconfigobj, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                target_metadata_schema='p2881_target_validation_schema.json')
            xiaconfigobj.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.schema_data_dict
            return_from_function = get_target_validation_schema()
            self.assertEqual(read_obj.return_value,
                             return_from_function)

    def test_get_target_metadata_for_transformation(self):
        """Test to retrieve target metadata schema from XIA configuration """
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xia_config_obj, \
                patch('core.management.utils.xss_client'
                      '.read_json_data') as read_obj:
            xiaConfig = XIAConfiguration(
                target_metadata_schema='AGENT_p2881_target_metadata_schema' +
                '.json',
                source_metadata_schema='AGENT_p2881_target_metadata_schema' +
                '.json'
            )
            xia_config_obj.return_value = xiaConfig
            read_obj.return_value = read_obj
            read_obj.return_value = self.target_data_dict
            return_from_function = get_target_metadata_for_transformation()
            self.assertEqual(read_obj.return_value,
                             return_from_function)

    def test_xss_get(self):
        """Test for retrieving XSS api root """
        with patch('core.management.utils.xss_client'
                   '.XIAConfiguration.objects') as xia_config_obj:
            xss_api = "http://test_xss_api"
            xiaConfig = XIAConfiguration(
                target_metadata_schema='AGENT_p2881_target_metadata_schema' +
                '.json',
                source_metadata_schema='AGENT_p2881_target_metadata_schema' +
                '.json',
                xss_api=xss_api
            )
            xia_config_obj.first.return_value = xiaConfig

            self.assertEqual(xss_get(), xss_api)

    def test_read_json_data(self):
        """Test for retrieving XSS json schemas """
        with patch('core.management.utils.xss_client.xss_get') as \
            xss_host, patch('core.management.utils.xss_client.'
                            'requests') as req:
            xss_api = "http://test_xss_api"
            schema = {"schema": {"test": "val"}}
            xss_host.return_value = xss_api
            req.get.return_value = req
            req.json.return_value = schema

            self.assertEqual(read_json_data(""), schema['schema'])

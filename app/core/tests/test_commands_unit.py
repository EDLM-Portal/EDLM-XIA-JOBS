import logging
from unittest.mock import patch

import pandas as pd
from ddt import ddt
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import tag
from django.utils import timezone

from core.management.commands.extract_source_metadata import (
    add_publisher_to_source, extract_metadata_using_key, get_source_metadata)
from core.management.commands.transform_source_metadata import (
    get_metadata_fields_to_overwrite, get_source_metadata_for_transformation,
    overwrite_append_metadata, overwrite_metadata_field,
    transform_source_using_key, type_checking_target_metadata)
from core.management.commands.validate_source_metadata import (
    get_source_metadata_for_validation,
    store_source_metadata_validation_status, validate_source_using_key)
from core.management.commands.validate_target_metadata import (
    get_target_metadata_for_validation, update_previous_instance_in_metadata,
    validate_target_using_key)
from core.models import (MetadataFieldOverwrite, MetadataLedger,
                         XIAConfiguration)

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class CommandTests(TestSetUp):

    # Test cases for waitdb
    def test_wait_for_db_ready(self):
        """Test that waiting for db when db is available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = gi
            gi.ensure_connection.return_value = True
            call_command('waitdb')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = gi
            gi.ensure_connection.side_effect = [OperationalError] * 5 + [True]
            call_command('waitdb')
            self.assertEqual(gi.ensure_connection.call_count, 6)

    # Test cases for extract_source_metadata
    def test_get_source_metadata(self):
        """ Test to retrieving source metadata"""
        with patch('core.management.commands.extract_source_metadata'
                   '.read_source_file') as read_obj, patch(
            'core.management.commands.extract_source_metadata'
            '.extract_metadata_using_key', return_value=None) as \
                mock_extract_obj:
            read_obj.return_value = read_obj
            read_obj.return_value = [
                pd.DataFrame.from_dict(self.test_data, orient='index')]
            get_source_metadata()
            self.assertEqual(mock_extract_obj.call_count, 1)

    def test_add_publisher_to_source(self):
        """Test for Add publisher column to source metadata and return
        source metadata"""
        with patch('core.management.utils.xia_internal'
                   '.get_publisher_detail'), \
                patch('core.management.utils.xia_internal'
                      '.XIAConfiguration.objects') as xisCfg:
            xiaConfig = XIAConfiguration(publisher='JKO')
            xisCfg.first.return_value = xiaConfig
            test_df = pd.DataFrame.from_dict(self.test_data)
            result = add_publisher_to_source(test_df)
            key_exist = 'SOURCESYSTEM' in result.columns
            self.assertTrue(key_exist)

    def test_extract_metadata_using_key(self):
        """Test to creating key, hash of key & hash of metadata"""

        data = {1: self.source_metadata}
        data_df = pd.DataFrame.from_dict(data, orient='index')
        with patch(
                'core.management.commands.extract_source_metadata'
                '.add_publisher_to_source',
                return_value=data_df), \
                patch(
                    'core.management.commands.extract_source_metadata'
                    '.get_source_metadata_key_value',
                    return_value=None) as mock_get_source, \
                patch(
                    'core.management.commands.extract_source_metadata'
                    '.store_source_metadata',
                    return_value=None) as mock_store_source:
            mock_get_source.return_value = mock_get_source
            mock_get_source.exclude.return_value = mock_get_source
            mock_get_source.filter.side_effect = [
                mock_get_source, mock_get_source]

            extract_metadata_using_key(data_df)
            self.assertEqual(mock_get_source.call_count, 1)
            self.assertEqual(mock_store_source.call_count, 1)

    # Test cases for validate_source_metadata

    def test_get_source_metadata_for_validation(self):
        """Test to Retrieving source metadata from MetadataLedger that needs
        to be validated"""
        with patch('core.management.commands.'
                   'validate_source_metadata.MetadataLedger.objects') \
                as meta_obj:
            meta_ledger = MetadataLedger.objects.values(
                source_metadata=self.source_metadata).filter(
                source_metadata_validation_status='',
                record_lifecycle_status='Active').exclude(
                source_metadata_extraction_date=None)
            meta_obj.first.return_value = meta_ledger
            return_from_function = get_source_metadata_for_validation()
            self.assertEqual(meta_obj.first.return_value, return_from_function)

    def test_validate_source_using_key_more_than_one(self):
        """Test to Validating source data against required & recommended
        column names for more than one row"""
        data = [{'source_metadata_key_hash': 123,
                 'source_metadata': self.source_metadata},
                {'source_metadata_key_hash': 123,
                 'source_metadata': self.source_metadata}]

        recommended_column_name = []
        with patch('core.management.commands.'
                   'validate_source_metadata'
                   '.store_source_metadata_validation_status',
                   return_value=None) as mock_store_source_valid_status:
            validate_source_using_key(data, self.test_required_column_names,
                                      recommended_column_name)
            self.assertEqual(
                mock_store_source_valid_status.call_count, 2)

    def test_validate_source_using_key_more_than_zero(self):
        """Test to Validating source data against required/ recommended column
            names with no data"""
        data = []
        recommended_column_name = []
        with patch('core.management.commands.'
                   'validate_source_metadata'
                   '.store_source_metadata_validation_status',
                   return_value=None) as mock_store_source_valid_status:
            validate_source_using_key(data, self.test_required_column_names,
                                      recommended_column_name)
            self.assertEqual(
                mock_store_source_valid_status.call_count, 0)

    def test_store_source_metadata_validation_status_valid(self):
        """Test to store source metadata with validation details"""

        metadata_ledger = MetadataLedger(
            record_lifecycle_status='Active',
            source_metadata=self.source_metadata,
            source_metadata_hash=self.hash_value,
            source_metadata_key=self.key_value,
            source_metadata_key_hash=self.key_value_hash,
            source_metadata_extraction_date=timezone.now())
        metadata_ledger.save()

        source_data_dict = \
            MetadataLedger.objects.values('source_metadata_key_hash',
                                          'source_metadata').filter(
                source_metadata_validation_status='',
                record_lifecycle_status='Active').exclude(
                source_metadata_extraction_date=None)

        store_source_metadata_validation_status(
            source_data_dict, self.key_value_hash, 'Y',
            'Active', self.source_metadata)

        result_metadata = \
            MetadataLedger.objects.values(
                "source_metadata_validation_status",
                "source_metadata_validation_date").filter(
                source_metadata_key_hash=self.key_value_hash,
                record_lifecycle_status='Active').first()

        self.assertEqual('Y',
                         result_metadata['source_metadata_validation_status'])
        self.assertTrue(result_metadata['source_metadata_validation_date'])

    def test_store_source_metadata_validation_status_invalid(self):
        """Test to store source metadata with validation details"""

        metadata_ledger = MetadataLedger(
            record_lifecycle_status='Active',
            source_metadata=self.source_metadata,
            source_metadata_hash=self.hash_value,
            source_metadata_key=self.key_value,
            source_metadata_key_hash=self.key_value_hash,
            source_metadata_extraction_date=timezone.now())
        metadata_ledger.save()

        source_data_dict = \
            MetadataLedger.objects.values('source_metadata_key_hash',
                                          'source_metadata').filter(
                source_metadata_validation_status='',
                record_lifecycle_status='Active').exclude(
                source_metadata_extraction_date=None)

        store_source_metadata_validation_status(
            source_data_dict, self.key_value_hash, 'N',
            'Inactive', self.source_metadata)

        result_metadata = \
            MetadataLedger.objects.values(
                "source_metadata_validation_status",
                "source_metadata_validation_date",
                "metadata_record_inactivation_date").filter(
                source_metadata_key_hash=self.key_value_hash).first()

        self.assertEqual('N',
                         result_metadata['source_metadata_validation_status'])
        self.assertTrue(result_metadata['source_metadata_validation_date'])
        self.assertTrue(result_metadata['metadata_record_inactivation_date'])

    # Test cases for transform_source_metadata

    def test_type_checking_target_metadata(self):
        """"Test function for type checking and explicit type conversion of
        metadata """
        target_metadata = {
            0: self.target_metadata}
        target_metadata = type_checking_target_metadata(1, target_metadata,
                                                        self.expected_datatype)
        self.assertIsInstance(target_metadata[0]['General_Information'][
                                  "EndDate"], str)

    def test_get_source_metadata_for_transformation(self):
        """Test to Retrieving Source metadata from MetadataLedger that needs
        to be transformed"""
        with patch('core.management.commands.'
                   'transform_source_metadata'
                   '.MetadataLedger.objects') as meta_obj:
            target_data_dict = MetadataLedger.objects.values(
                source_data_dict=self.source_metadata).filter(
                source_metadata_validation_status='Y',
                record_lifecycle_status='Active').exclude(
                source_metadata_validation_date=None)
            meta_obj.first.return_value = target_data_dict
            return_from_function = get_source_metadata_for_transformation()
            self.assertEqual(meta_obj.first.return_value,
                             return_from_function)

    def test_transform_source_using_key_more_zero(self):
        """Test for transforming source data using target metadata schema
        with no data"""
        data = []
        with patch('core.management.utils.xia_internal'
                   '.get_target_metadata_key_value',
                   return_value=None), \
                patch('core.management.commands.'
                      'transform_source_metadata'
                      '.store_transformed_source_metadata',
                      return_value=None) as mock_store_transformed_source:
            mock_store_transformed_source.return_value = \
                mock_store_transformed_source
            mock_store_transformed_source.exclude.return_value = \
                mock_store_transformed_source
            mock_store_transformed_source.filter.side_effect = [
                mock_store_transformed_source, mock_store_transformed_source]

            transform_source_using_key(data, self.source_target_mapping,
                                       self.test_required_column_names,
                                       self.expected_datatype)

            self.assertEqual(
                mock_store_transformed_source.call_count, 0)

    def test_overwrite_metadata_field(self):
        """Test to overwrite metadata with admin entered values and
        return metadata in dictionary format """

        with patch('core.management.commands.transform_source_metadata'
                   '.get_metadata_fields_to_overwrite') as mock_get_overwrite:
            mock_get_overwrite.return_value = self.metadata_df

            return_val = overwrite_metadata_field(self.metadata_df)
            self.assertIsInstance(return_val, dict)

    def test_get_metadata_fields_to_overwrite(self):
        """Test for looping through fields to be overwrite or appended"""
        with patch('core.management.commands.'
                   'transform_source_metadata.MetadataFieldOverwrite.'
                   'objects') as mock_field, \
                patch('core.management.commands.'
                      'transform_source_metadata.'
                      'overwrite_append_metadata') as mock_overwrite_fun:
            config = \
                [MetadataFieldOverwrite(field_name='column1', overwrite=True,
                                        field_value='value1'),
                 MetadataFieldOverwrite(field_name='column2', overwrite=False,
                                        field_value='value2')]
            mock_field.all.return_value = config
            mock_overwrite_fun.return_value = self.metadata_df

            get_metadata_fields_to_overwrite(self.metadata_df)
            self.assertEqual(mock_overwrite_fun.call_count, 2)

    def test_overwrite_append_metadata(self):
        """test Overwrite & append metadata fields based on overwrite flag """
        return_val = \
            overwrite_append_metadata(self.metadata_df, 'column_1', 'value_1',
                                      True)

        self.assertEqual(return_val['column_1'][0], 'value_1')

    # Test cases for validate_target_metadata

    def test_get_target_metadata_for_validation(self):
        """Test to Retrieving target metadata from MetadataLedger that needs
        to be validated"""
        with patch('core.management.commands.'
                   'validate_target_metadata.MetadataLedger.objects') \
                as meta_obj:
            target_data_dict = MetadataLedger.objects.values(
                target_metadata=self.target_metadata).filter(
                target_metadata_validation_status='',
                record_lifecycle_status='Active').exclude(
                source_metadata_transformation_date=None)
            meta_obj.first.return_value = target_data_dict
            return_from_function = get_target_metadata_for_validation()
            self.assertEqual(meta_obj.first.return_value,
                             return_from_function)

    def test_validate_target_using_key_more_than_one(self):
        """Test to Validating target data against required & recommended
        column names for more than one row"""
        data = [{'target_metadata_key_hash': 123,
                 'target_metadata': self.target_metadata},
                {'target_metadata_key_hash': 123,
                 'target_metadata': self.target_metadata}]
        test_required_column_names = {
            'CourseInstance.EndDate', 'CourseInstance.DeliveryMode',
            'CourseInstance.CourseCode', 'CourseInstance.Instructor',
            'Course.CourseProviderName', 'Course.CourseDescription',
            'Course.CourseShortDescription', 'CourseInstance.StartDate',
            'Course.CourseCode', 'CourseInstance.CourseTitle ',
            'General_Information.StartDate', 'Course.CourseSubjectMatter',
            'General_Information.EndDate', 'Course.CourseTitle',
            'Technical.CourseTitle'}
        recommended_column_name = {'Technical_Information.Thumbnail',
                                   'CourseInstance.Thumbnail'}
        with patch('core.management.commands.'
                   'validate_target_metadata'
                   '.store_target_metadata_validation_status',
                   return_value=None) as mock_store_target_valid_status:
            validate_target_using_key(data, test_required_column_names,
                                      recommended_column_name,
                                      self.expected_datatype)
            self.assertEqual(
                mock_store_target_valid_status.call_count, 2)

    def test_validate_target_using_key_zero(self):
        """Validating target data against required & recommended column names
        with no data"""

        data = []

        with patch('core.management.commands.'
                   'validate_target_metadata'
                   '.store_target_metadata_validation_status',
                   return_value=None) as mock_store_target_valid_status:
            validate_target_using_key(data,
                                      self.test_target_required_column_names,
                                      self.recommended_column_name,
                                      self.expected_datatype)

            self.assertEqual(mock_store_target_valid_status.call_count, 0)

    def test_update_previous_instance_in_metadata(self):
        """test to check Update older instances of record to inactive status"""
        metadata = MetadataLedger(source_metadata=self.source_metadata,
                                  target_metadata=self.target_metadata,
                                  target_metadata_key=self.target_key_value,
                                  target_metadata_key_hash=self.
                                  target_key_value_hash,
                                  source_metadata_key_hash=self.
                                  target_key_value_hash,
                                  target_metadata_hash=self.target_hash_value,
                                  record_lifecycle_status='Active',
                                  target_metadata_validation_date=timezone.
                                  now())
        metadata.save()
        update_previous_instance_in_metadata(self.key_value_hash)

        updated_value = MetadataLedger.objects. \
            get(target_metadata_key_hash=self.target_key_value_hash)
        self.assertEqual(updated_value.record_lifecycle_status, 'Inactive')

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.utils import timezone

from core.models import (MetadataFieldOverwrite, MetadataLedger,
                         XIAConfiguration, XISConfiguration, XSRConfiguration)


@tag('unit')
class ModelTests(TestCase):

    def test_create_xsr_configuration(self):
        """Test that creating a new XSR Configuration entry is successful
        with defaults """
        xsr_api_endpoint = 'api/test_file'

        xiaConfig = XSRConfiguration(
            xsr_api_endpoint=xsr_api_endpoint)

        self.assertEqual(xiaConfig.xsr_api_endpoint,
                         xsr_api_endpoint)

    def test_create_xia_configuration(self):
        """Test that creating a new XIA Configuration entry is successful
        with defaults """
        source_metadata_schema = 'test_file.json'
        xss_api = 'https://localhost'
        target_metadata_schema = 'test_file.json'

        xiaConfig = XIAConfiguration(
            source_metadata_schema=source_metadata_schema,
            xss_api=xss_api,
            target_metadata_schema=target_metadata_schema)

        self.assertEqual(xiaConfig.source_metadata_schema,
                         source_metadata_schema)
        self.assertEqual(xiaConfig.xss_api, xss_api)
        self.assertEqual(xiaConfig.target_metadata_schema,
                         target_metadata_schema)

    def test_create_two_xia_configuration(self):
        """Test that trying to create more than one XIS Configuration throws
        ValidationError """
        with patch("core.models.XIAConfiguration.field_overwrite"):
            with self.assertRaises(ValidationError):
                xiaConfig = \
                    XIAConfiguration(source_metadata_schema="example1.json",
                                     xss_api="https://localhost",
                                     target_metadata_schema="example1.json")
                xiaConfig2 = \
                    XIAConfiguration(source_metadata_schema="example2.json",
                                     xss_api="https://localhost",
                                     target_metadata_schema="example2.json")
                xiaConfig.save()
                xiaConfig2.save()

    def test_xia_field_overwrite(self):
        """Test that field_overwrite in an XIA Configuration generates
        MetadataFieldOverwrite objects """
        with patch("core.models.requests") as mock:
            target_schema = {"schema": {
                "start": {"test": {"use": "Required"}}}}
            transform_schema = {"schema_mapping": {
                "start": {"test": "start.test"}}}
            mock.get.return_value = mock
            mock.json.side_effect = [target_schema, transform_schema]
            xiaConfig = \
                XIAConfiguration(source_metadata_schema="example1.json",
                                 xss_api="https://localhost",
                                 target_metadata_schema="example1.json")
            xiaConfig.save()
            self.assertEqual(MetadataFieldOverwrite.objects.count(), 1)

    def test_create_xis_configuration(self):
        """Test that creating a new XIS Configuration entry is successful
        with defaults """
        xis_metadata_api_endpoint = 'http://localhost:8000/api/metadata/'
        xis_api_key = 'token'

        xisConfig = XISConfiguration(
            xis_metadata_api_endpoint=xis_metadata_api_endpoint,
            xis_api_key=xis_api_key)

        self.assertEqual(xisConfig.xis_api_key,
                         xis_api_key)
        self.assertEqual(xisConfig.xis_api_key,
                         xis_api_key)

    def test_create_two_xis_configuration(self):
        """Test that creating trying to create more than one XIS Configuration
        throws a ValidationError """
        xis_metadata_api_endpoint = 'http://localhost:8000/api/metadata/'
        xis_api_key = 'http://localhost:8000/api/supplement/'

        xisConfig = XISConfiguration(
            xis_metadata_api_endpoint=xis_metadata_api_endpoint,
            xis_api_key=xis_api_key)
        xisConfig2 = XISConfiguration(
            xis_metadata_api_endpoint=xis_metadata_api_endpoint,
            xis_api_key=xis_api_key)

        with self.assertRaises(ValidationError):
            xisConfig.save()
            xisConfig2.save()

    def test_metadata_ledger(self):
        """Test for a new Metadata_Ledger entry is successful with defaults"""
        metadata_record_inactivate_date = timezone.now()
        record_lifecycle_status = 'Active'
        source_metadata = ''
        source_metadata_extraction_date = ''
        source_metadata_hash = '74df499f177d0a7adb3e610302abc6a5'
        source_metadata_key = 'AGENT_test_key'
        source_metadata_key_hash = 'f6df40fbbf4a4c4091fbf64c9b6458e0'
        source_metadata_transform_date = timezone.now()
        source_metadata_validation_date = timezone.now()
        source_metadata_valid_status = 'Y'
        target_metadata = ''
        target_metadata_hash = '74df499f177d0a7adb3e610302abc6a5'
        target_metadata_key = 'AGENT_test_key'
        target_metadata_key_hash = '74df499f177d0a7adb3e610302abc6a5'
        target_metadata_transmit_date = timezone.now()
        target_meta_transmit_status = 'Ready'
        target_transmit_st_code = 200
        target_metadata_validation_date = timezone.now()
        target_metadata_validation_status = 'Y'

        metadataLedger = MetadataLedger(
            metadata_record_inactivation_date=metadata_record_inactivate_date,
            record_lifecycle_status=record_lifecycle_status,
            source_metadata=source_metadata,
            source_metadata_extraction_date=source_metadata_extraction_date,
            source_metadata_hash=source_metadata_hash,
            source_metadata_key=source_metadata_key,
            source_metadata_key_hash=source_metadata_key_hash,
            source_metadata_transformation_date=source_metadata_transform_date,
            source_metadata_validation_date=source_metadata_validation_date,
            source_metadata_validation_status=source_metadata_valid_status,
            target_metadata=target_metadata,
            target_metadata_hash=target_metadata_hash,
            target_metadata_key=target_metadata_key,
            target_metadata_key_hash=target_metadata_key_hash,
            target_metadata_transmission_date=target_metadata_transmit_date,
            target_metadata_transmission_status=target_meta_transmit_status,
            target_metadata_transmission_status_code=target_transmit_st_code,
            target_metadata_validation_date=target_metadata_validation_date,
            target_metadata_validation_status=target_metadata_validation_status
        )

        self.assertEqual(metadataLedger.metadata_record_inactivation_date,
                         metadata_record_inactivate_date)
        self.assertEqual(metadataLedger.record_lifecycle_status,
                         record_lifecycle_status)
        self.assertEqual(metadataLedger.source_metadata, source_metadata)
        self.assertEqual(metadataLedger.source_metadata_extraction_date,
                         source_metadata_extraction_date)
        self.assertEqual(metadataLedger.source_metadata_hash,
                         source_metadata_hash)
        self.assertEqual(metadataLedger.source_metadata_key,
                         source_metadata_key)
        self.assertEqual(metadataLedger.source_metadata_key_hash,
                         source_metadata_key_hash)
        self.assertEqual(metadataLedger.source_metadata_transformation_date,
                         source_metadata_transform_date)
        self.assertEqual(metadataLedger.source_metadata_validation_date,
                         source_metadata_validation_date)
        self.assertEqual(metadataLedger.source_metadata_validation_status,
                         source_metadata_valid_status)
        self.assertEqual(metadataLedger.target_metadata, target_metadata)
        self.assertEqual(metadataLedger.target_metadata_hash,
                         target_metadata_hash)
        self.assertEqual(metadataLedger.target_metadata_key,
                         target_metadata_key)
        self.assertEqual(metadataLedger.target_metadata_key_hash,
                         target_metadata_key_hash)
        self.assertEqual(metadataLedger.target_metadata_transmission_date,
                         target_metadata_transmit_date)
        self.assertEqual(metadataLedger.target_metadata_transmission_status,
                         target_meta_transmit_status)
        self.assertEqual(
            metadataLedger.target_metadata_transmission_status_code,
            target_transmit_st_code)
        self.assertEqual(metadataLedger.target_metadata_validation_date,
                         target_metadata_validation_date)
        self.assertEqual(metadataLedger.target_metadata_validation_status,
                         target_metadata_validation_status)

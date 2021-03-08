from django.test import SimpleTestCase
from core.models import XIAConfiguration
from core.models import MetadataLedger
from django.test import tag


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_xia_configuration(self):
        """Test that creating a new XIA Configuration entry is successful
        with defaults """
        source_metadata_schema = 'test_file.csv'

        xiaConfig = XIAConfiguration(source_metadata_schema=source_metadata_schema)

        self.assertEqual(xiaConfig.source_metadata_schema, source_metadata_schema)
        self.assertEqual(xiaConfig.source_target_mapping,
                         'p2881_target_metadata_schema.json')
        self.assertEqual(xiaConfig.target_metadata_schema,
                         'p2881_target_validation_schema.json')

    def test_metadata_ledger(self):
        """Test for a new Metadata_Ledger entry is successful with defaults"""
        metadata_record_inactivation_date = '2021-02-04 01:26:56.528476'
        # metadata_record_uuid = ''
        record_lifecycle_status = 'A'
        source_metadata = ''
        source_metadata_extraction_date = '2021-03-08 15:57:05.458400'
        source_metadata_hash = '74df499f177d0a7adb3e610302abc6a5'
        source_metadata_key = 'DAU_SS-cl_amas_a01_it_enus'
        source_metadata_key_hash = 'f6df40fbbf4a4c4091fbf64c9b6458e0'
        source_metadata_transformation_date = '2021-02-04 01:26:56.528476'
        source_metadata_validation_date = '2021-02-04 01:26:56.528476'
        source_metadata_validation_status = 'Y'
        target_metadata = ''
        target_metadata_hash = '74df499f177d0a7adb3e610302abc6a5'
        target_metadata_key = 'DAU_SS-cl_amas_a01_it_enus'
        target_metadata_key_hash = '74df499f177d0a7adb3e610302abc6a5'
        target_metadata_transmission_date = '2021-02-04 01:26:56.528476'
        target_metadata_transmission_status = 'Ready'
        target_metadata_transmission_status_code = ''
        target_metadata_validation_date = '2021-02-04 01:26:56.528476'
        target_metadata_validation_status = 'Y'

        metadataLedger = MetadataLedger(
            metadata_record_inactivation_date=
            metadata_record_inactivation_date,
            # metadata_record_uuid=metadata_record_uuid,
            record_lifecycle_status=record_lifecycle_status,
            source_metadata=source_metadata,
            source_metadata_extraction_date=source_metadata_extraction_date,
            source_metadata_hash=source_metadata_hash,
            source_metadata_key=source_metadata_key,
            source_metadata_key_hash=source_metadata_key_hash,

            source_metadata_transformation_date=
            source_metadata_transformation_date,
            source_metadata_validation_date=source_metadata_validation_date,
            source_metadata_validation_status=
            source_metadata_validation_status,
            target_metadata=target_metadata,
            target_metadata_hash=target_metadata_hash,
            target_metadata_key=target_metadata_key,
            target_metadata_key_hash=target_metadata_key_hash,
            target_metadata_transmission_status=
            target_metadata_transmission_status,
            target_metadata_transmission_date=
            target_metadata_transmission_date,
            target_metadata_transmission_status_code=
            target_metadata_transmission_status_code,
            target_metadata_validation_date=target_metadata_validation_date,
            target_metadata_validation_status=
            target_metadata_validation_status)

        # self.assertEqual(metadataLedger.metadata_record_uuid,
        #                  metadata_record_uuid)
        self.assertEqual(metadataLedger.metadata_record_inactivation_date,
                         metadata_record_inactivation_date)
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
                         source_metadata_transformation_date)
        self.assertEqual(metadataLedger.source_metadata_validation_date,
                         source_metadata_validation_date)
        self.assertEqual(metadataLedger.source_metadata_validation_status,
                         source_metadata_validation_status)
        self.assertEqual(metadataLedger.target_metadata, target_metadata)
        self.assertEqual(metadataLedger.target_metadata_hash,
                         target_metadata_hash)
        self.assertEqual(metadataLedger.target_metadata_key,
                         target_metadata_key)
        self.assertEqual(metadataLedger.target_metadata_key_hash,
                         target_metadata_key_hash)
        self.assertEqual(metadataLedger.target_metadata_transmission_date,
                         target_metadata_transmission_date)
        self.assertEqual(metadataLedger.
                         target_metadata_transmission_status_code,
                         target_metadata_transmission_status_code)
        self.assertEqual(metadataLedger.target_metadata_transmission_status,
                         target_metadata_transmission_status)
        self.assertEqual(metadataLedger.target_metadata_validation_date,
                         target_metadata_validation_date)
        self.assertEqual(metadataLedger.target_metadata_validation_status,
                         target_metadata_validation_status)

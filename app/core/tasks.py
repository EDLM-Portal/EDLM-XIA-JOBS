import logging

from celery import shared_task
from openlxp_notifications.management.commands.trigger_status_update import \
    Command as conformance_alerts_Command

from core.management.commands.extract_source_metadata import \
    Command as extract_Command
from core.management.commands.load_target_metadata import \
    Command as load_Command
from core.management.commands.transform_source_metadata import \
    Command as transform_Command
from core.management.commands.validate_source_metadata import \
    Command as validate_source_Command
from core.management.commands.validate_target_metadata import \
    Command as validate_target_Command

logger = logging.getLogger('dict_config_logger')


@shared_task(name="workflow_for_xia")
def execute_xia_automated_workflow():
    """XIA automated workflow"""
    logger.info('STARTING WORKFLOW')

    extract_class = extract_Command()
    validate_source_class = validate_source_Command()
    transform_class = transform_Command()
    validate_target_class = validate_target_Command()
    load_class = load_Command()
    conformance_alerts_class = conformance_alerts_Command()

    conformance_alerts_class.handle(email_references="Status_update")
    extract_class.handle()
    validate_source_class.handle()
    transform_class.handle()
    validate_target_class.handle()
    load_class.handle()

    logger.info('COMPLETED WORKFLOW')

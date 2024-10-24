import logging

from rest_framework import serializers

from .models import MetadataLedger

logger = logging.getLogger(__name__)


class MetadataLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataLedger
        fields = ["Value", "Code"]

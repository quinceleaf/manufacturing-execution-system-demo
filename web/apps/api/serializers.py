from rest_framework import generics, permissions, serializers

from apps.common import models as common_models
from apps.masterdata import models as masterdata_models


# MASTERDATA SERIALIZERS


class BillOfMaterialsLineSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.BillOfMaterialsLine


class ItemSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.Item


class MaterialSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.Material


class ProductSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.Product


class ResourceSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.Resource


class TeamSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.Team


class UnitMeasurementSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = masterdata_models.UnitMeasurement


#

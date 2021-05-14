# ––– DJANGO IMPORTS
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone


# ––– PYTHON UTILITY IMPORTS
import datetime as dt
from decimal import Decimal
import json
import re


# ––– THIRD-PARTY IMPORTS
from rest_framework import (
    exceptions,
    generics,
    permissions,
    serializers,
    status,
    views,
    viewsets,
    filters,
)
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# ––– APPLICATION IMPORTS
from apps.api import serializers as api_serializers
from apps.common import models as common_models
from apps.masterdata import models as masterdata_models


# MASTERDATA MODELS


class BillOfMaterialsLineSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.BillOfMaterialsLine.objects.all()
    serializer_class = api_serializers.BillOfMaterialsLineSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.BillOfMaterialsLine.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class ItemSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.Item.objects.all()
    serializer_class = api_serializers.ItemSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.Item.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class MaterialSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.Material.objects.all()
    serializer_class = api_serializers.MaterialSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.Material.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class ProductSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.Product.objects.all()
    serializer_class = api_serializers.ProductSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.Product.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class ResourceSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.Resource.objects.all()
    serializer_class = api_serializers.ResourceSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.Resource.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class TeamSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.Team.objects.all()
    serializer_class = api_serializers.TeamSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.Team.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UnitMeasurementSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.UnitMeasurement.objects.all()
    serializer_class = api_serializers.UnitMeasurementSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.UnitMeasurement.objects.all()

        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(symbol__icontains=search_term)
            )

        material_term = self.request.query_params.get("m", None)
        if material_term is not None:
            try:
                m = masterdata_models.Item.objects.get(id=material_term)
                qs = qs.filter(unit_type=m.unit_type)
            except:
                pass

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UnitMeasurementAppropriateSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.UnitMeasurement.objects.all()
    serializer_class = api_serializers.UnitMeasurementSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.UnitMeasurement.objects.all()

        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            try:
                m = masterdata_models.Item.objects.get(id=search_term)
                qs = qs.filter(unit_type=m.unit_type)
            except:
                pass

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UnitMeasurementWeightSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.UnitMeasurement.objects.filter(unit_type="WEIGHT")
    serializer_class = api_serializers.UnitMeasurementSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.UnitMeasurement.objects.filter(unit_type="WEIGHT")
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(symbol__icontains=search_term)
            )

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UnitMeasurementVolumeSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.UnitMeasurement.objects.filter(unit_type="VOLUME")
    serializer_class = api_serializers.UnitMeasurementSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.UnitMeasurement.objects.filter(unit_type="VOLUME")
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(symbol__icontains=search_term)
            )

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UnitMeasurementEachSelectAPIView(generics.ListAPIView):
    queryset = masterdata_models.UnitMeasurement.objects.filter(unit_type="EACH")
    serializer_class = api_serializers.UnitMeasurementSelectSerializer

    def get(self, request, format=None):
        qs = masterdata_models.UnitMeasurement.objects.filter(unit_type="EACH")
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(symbol__icontains=search_term)
            )

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)

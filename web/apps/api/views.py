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
from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# ––– APPLICATION IMPORTS
from apps.api import pagination, serializers as api_serializers
from apps.common import models as common_models
from apps.masterdata import (
    models as masterdata_models,
    selectors as masterdata_selectors,
    services as masterdata_services,
)


# TODO: Authentication for API

""" 
Naming convention: <Entity><Action>Api
"""

# MASTERDATA VIEWS


class MaterialListApi(APIView):
    class Pagination(pagination.LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.CharField(required=False)
        name = serializers.CharField(required=False)
        category = serializers.CharField(required=False)
        unit_type = serializers.CharField(required=False)
        state = serializers.CharField(required=False)
        notes = serializers.CharField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Material
            fields = (
                "id",
                "name",
                "category",
                "unit_type",
                "state",
                "notes",
            )

    # def get(self, request):
    #     materials = masterdata_selectors.material_list()
    #     print("materials:", materials)

    #     data = self.OutputSerializer(materials, many=True).data

    #     return Response(data)

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        materials = masterdata_selectors.material_list(
            filters=filters_serializer.validated_data
        )

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=materials,
            request=request,
            view=self,
        )


class MaterialDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Material
            fields = (
                "id",
                "name",
                "category",
                "unit_type",
                "state",
                "notes",
            )

    def get(self, request, material_id):
        material = masterdata_selectors.material_detail(material_id=material_id)

        serializer = self.OutputSerializer(material)

        return Response(serializer.data)


class MaterialCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()
        unit_type = serializers.CharField()
        state = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.material_create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class MaterialUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()
        unit_type = serializers.CharField()
        state = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request, material_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.material_update(
            material_id=material_id, **serializer.validated_data
        )

        return Response(status=status.HTTP_200_OK)


class MaterialActionApi(APIView):
    pass


class ProductListApi(APIView):
    class Pagination(pagination.LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.CharField(required=False)
        name = serializers.CharField(required=False)
        category = serializers.CharField(required=False)
        unit_type = serializers.CharField(required=False)
        state = serializers.CharField(required=False)
        notes = serializers.CharField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Product
            fields = (
                "id",
                "name",
                "category",
                "unit_type",
                "state",
                "notes",
            )

    # def get(self, request):
    #     products = masterdata_selectors.product_list()
    #     print("products:", products)

    #     data = self.OutputSerializer(products, many=True).data

    #     return Response(data)

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        products = masterdata_selectors.product_list(
            filters=filters_serializer.validated_data
        )

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=products,
            request=request,
            view=self,
        )


class ProductDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Product
            fields = (
                "id",
                "name",
                "category",
                "unit_type",
                "state",
                "notes",
            )

    def get(self, request, product_id):
        product = masterdata_selectors.product_detail(product_id=product_id)

        serializer = self.OutputSerializer(product)

        return Response(serializer.data)


class ProductCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()
        unit_type = serializers.CharField()
        state = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.product_create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class ProductUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()
        unit_type = serializers.CharField()
        state = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request, product_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.product_update(
            product_id=product_id, **serializer.validated_data
        )

        return Response(status=status.HTTP_200_OK)


class ProductActionApi(APIView):
    pass


class ResourceListApi(APIView):
    class Pagination(pagination.LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.CharField(required=False)
        name = serializers.CharField(required=False)
        capacity = serializers.CharField(required=False)
        unit = serializers.CharField(required=False)
        resource_type = serializers.CharField(required=False)
        stage = serializers.CharField(required=False)
        notes = serializers.CharField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Resource
            fields = (
                "id",
                "name",
                "capacity",
                "unit",
                "resource_type",
                "stage",
                "notes",
            )

    # def get(self, request):
    #     resources = masterdata_selectors.resource_list()
    #     print("resources:", resources)

    #     data = self.OutputSerializer(resources, many=True).data

    #     return Response(data)

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        resources = masterdata_selectors.resource_list(
            filters=filters_serializer.validated_data
        )

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=resources,
            request=request,
            view=self,
        )


class ResourceDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Resource
            fields = (
                "id",
                "name",
                "capacity",
                "unit",
                "resource_type",
                "stage",
                "notes",
            )

    def get(self, request, resource_id):
        resource = masterdata_selectors.resource_detail(resource_id=resource_id)

        serializer = self.OutputSerializer(resource)

        return Response(serializer.data)


class ResourceCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        capacity = serializers.CharField()
        unit = serializers.CharField()
        resource_type = serializers.CharField()
        stage = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.resource_create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class ResourceUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        capacity = serializers.CharField()
        unit = serializers.CharField()
        resource_type = serializers.CharField()
        stage = serializers.CharField()
        notes = serializers.CharField()

    def post(self, request, resource_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.resource_update(
            resource_id=resource_id, **serializer.validated_data
        )

        return Response(status=status.HTTP_200_OK)


class ResourceActionApi(APIView):
    pass


class TeamListApi(APIView):
    class Pagination(pagination.LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.CharField(required=False)
        name = serializers.CharField(required=False)
        slug = serializers.CharField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Team
            fields = ("id", "name", "slug")

    # def get(self, request):
    #     teams = masterdata_selectors.team_list()
    #     print("teams:", teams)

    #     data = self.OutputSerializer(teams, many=True).data

    #     return Response(data)

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        teams = masterdata_selectors.team_list(
            filters=filters_serializer.validated_data
        )

        return pagination.get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=teams,
            request=request,
            view=self,
        )


class TeamDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = masterdata_models.Team
            fields = ("id", "name", "slug")

    def get(self, request, team_id):
        team = masterdata_selectors.team_detail(team_id=team_id)

        serializer = self.OutputSerializer(team)

        return Response(serializer.data)


class TeamCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        slug = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.team_create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class TeamUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        slug = serializers.CharField()

    def post(self, request, team_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masterdata_services.team_update(team_id=team_id, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class TeamActionApi(APIView):
    pass

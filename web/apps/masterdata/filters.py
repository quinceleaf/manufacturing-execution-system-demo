from django.db.models import Q

import django_filters

from apps.masterdata import models


class MaterialListFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Material
        fields = ["name", "category"]


class MaterialListFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Material
        fields = ["name", "category", "state", "notes", "unit_type"]


class MaterialCharacteristicsBulkEditListFilterAdvanced(django_filters.FilterSet):

    INVENTORY_CATEGORY_CHOICES = (
        ("RAW", "Raw Food Ingredient"),
        ("PREPARED", "Prepared Food Ingredient"),
        ("SERVICE", "Service"),
        ("MRO", "Maintenance/Operating Supplies"),
        ("PACKAGING", "Packaging/Disposable"),
        ("OTHER", "Other/Misc"),
    )

    category = django_filters.ChoiceFilter(
        choices=INVENTORY_CATEGORY_CHOICES,
        label="Category",
        distinct=True,
    )

    class Meta:
        model = models.Material
        fields = [
            "name",
            "category",
        ]


class ProductListFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Product
        fields = ["name", "category"]


class ProductListFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Product
        fields = ["name", "category", "state", "notes", "unit_type"]


class ResourceListFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Resource
        fields = ["name"]


class ResourceListFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Resource
        fields = ["name", "capacity"]


class TeamListFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Team
        fields = ["name"]


class TeamListFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Team
        fields = ["name"]

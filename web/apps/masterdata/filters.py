# ––– DJANGO MODELS
from django.db.models import Q


# ––– THIRD-PARTY MODELS
import django_filters


# ––– APPLICATION IMPORTS
from apps.masterdata import models


class BillOfMaterialsFilterSimple(django_filters.FilterSet):

    product = django_filters.CharFilter(lookup_expr="name__icontains", distinct=True)

    class Meta:
        model = models.BillOfMaterials
        fields = [
            "product",
        ]


class MaterialFilterSimple(django_filters.FilterSet):

    MATERIAL_VALID_CATEGORIES = (
        ("RAW", "Raw Food Ingredient"),
        ("PREPARED", "Prepared Food Ingredient"),
        ("SERVICE", "Service"),
        ("MRO", "Maintenance/Operating Supplies"),
        ("PACKAGING", "Packaging/Disposable"),
        ("OTHER", "Other/Misc"),
    )

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    category = django_filters.ChoiceFilter(choices=MATERIAL_VALID_CATEGORIES)

    class Meta:
        model = models.Material
        fields = ["name", "category"]


class MaterialFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Material
        fields = ["name", "category", "notes", "is_available", "unit_type"]


class MaterialCharacteristicsBulkEditFilterAdvanced(django_filters.FilterSet):

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


class ProductFilterSimple(django_filters.FilterSet):
    PRODUCT_VALID_CATEGORIES = (
        ("WIP", "Work-in-Progress"),
        ("FINISHED", "Finished Product"),
    )

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    category = django_filters.ChoiceFilter(choices=PRODUCT_VALID_CATEGORIES)

    class Meta:
        model = models.Product
        fields = ["name", "category"]


class ProductFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Product
        fields = [
            "name",
            "category",
            "notes",
            "is_available",
            "unit_type",
            "production_type",
        ]


class ResourceFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Resource
        fields = ["name"]


class ResourceFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Resource
        fields = ["name", "capacity"]


class TeamFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.Team
        fields = ["name"]


class TeamFilterAdvanced(django_filters.FilterSet):
    class Meta:
        model = models.Team
        fields = ["name"]


class UnitMeasurementFilterSimple(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    class Meta:
        model = models.UnitMeasurement
        fields = ["name", "symbol"]
from django.db.models import QuerySet
import django_filters

from apps.masterdata import models


# MATERIAL


class MaterialFilter(django_filters.FilterSet):
    class Meta:
        model = models.Material
        fields = (
            "id",
            "name",
            "category",
            "unit_type",
            "state",
            "notes",
        )


def material_list(*, filters=None) -> QuerySet[models.Material]:
    filters = filters or {}
    qs = models.Material.objects.all()
    return MaterialFilter(filters, qs).qs


def material_detail(*, material_id: str) -> models.Material:
    qs = models.Material.objects.get(id=material_id)
    return qs


def material_update(*, filters=None) -> QuerySet[models.Material]:
    pass


def material_delete(*, filters=None) -> QuerySet[models.Material]:
    pass


# PRODUCT


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = models.Product
        fields = (
            "id",
            "name",
            "category",
            "unit_type",
            "state",
            "notes",
        )


def product_list(*, filters=None) -> QuerySet[models.Product]:
    filters = filters or {}
    qs = models.Product.objects.all()
    return ProductFilter(filters, qs).qs


def product_detail(*, product_id: str) -> models.Product:
    qs = models.Product.objects.get(id=product_id)
    return qs


def product_update(*, filters=None) -> QuerySet[models.Product]:
    pass


def product_delete(*, filters=None) -> QuerySet[models.Product]:
    pass


# RESOURCE


class ResourceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Resource
        fields = ("id", "name", "capacity", "unit", "resource_type", "stage", "notes")


def resource_list(*, filters=None) -> QuerySet[models.Resource]:
    filters = filters or {}
    qs = models.Resource.objects.all()
    return ResourceFilter(filters, qs).qs


def resource_detail(*, resource_id: str) -> models.Resource:
    qs = models.Resource.objects.get(id=resource_id)
    return qs


def resource_update(*, filters=None) -> QuerySet[models.Resource]:
    pass


def resource_delete(*, filters=None) -> QuerySet[models.Resource]:
    pass


# TEAM


class TeamFilter(django_filters.FilterSet):
    class Meta:
        model = models.Team
        fields = ("id", "name", "slug")


def team_list(*, filters=None) -> QuerySet[models.Team]:
    filters = filters or {}
    qs = models.Team.objects.all()
    return TeamFilter(filters, qs).qs


def team_detail(*, team_id: str) -> models.Team:
    qs = models.Team.objects.get(id=team_id)
    return qs


def team_update(*, filters=None) -> QuerySet[models.Team]:
    pass


def team_delete(*, filters=None) -> QuerySet[models.Team]:
    pass
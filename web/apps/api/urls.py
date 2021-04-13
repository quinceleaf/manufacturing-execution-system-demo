from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.api import select_views, views
from apps.common import converters as common_converters

register_converter(common_converters.ULIDConverter, "ulid")
app_name = "apps.api"


""" MasterData app urls """
material_urls = [
    path(
        "<ulid:material_id>/edit/",
        views.MaterialUpdateApi.as_view(),
        name="material_edit",
    ),
    path(
        "<ulid:material_id>/action/",
        views.MaterialActionApi.as_view(),
        name="material_action",
    ),
    path(
        "<ulid:material_id>/",
        views.MaterialDetailApi.as_view(),
        name="material_detail",
    ),
    path(
        "add/",
        views.MaterialCreateApi.as_view(),
        name="material_add",
    ),
    path(
        "",
        views.MaterialListApi.as_view(),
        name="material_list",
    ),
]

product_urls = [
    path(
        "<ulid:product_id>/edit/",
        views.ProductUpdateApi.as_view(),
        name="product_edit",
    ),
    path(
        "<ulid:product_id>/action/",
        views.ProductActionApi.as_view(),
        name="product_action",
    ),
    path(
        "<ulid:product_id>/",
        views.ProductDetailApi.as_view(),
        name="product_detail",
    ),
    path(
        "add/",
        views.ProductCreateApi.as_view(),
        name="product_add",
    ),
    path(
        "",
        views.ProductListApi.as_view(),
        name="product_list",
    ),
]

resource_urls = [
    path(
        "<ulid:resource_id>/edit/",
        views.ResourceUpdateApi.as_view(),
        name="resource_edit",
    ),
    path(
        "<ulid:resource_id>/action/",
        views.ResourceActionApi.as_view(),
        name="resource_action",
    ),
    path(
        "<ulid:resource_id>/",
        views.ResourceDetailApi.as_view(),
        name="resource_detail",
    ),
    path(
        "add/",
        views.ResourceCreateApi.as_view(),
        name="resource_add",
    ),
    path(
        "",
        views.ResourceListApi.as_view(),
        name="resource_list",
    ),
]

team_urls = [
    path(
        "<ulid:team_id>/edit/",
        views.TeamUpdateApi.as_view(),
        name="team_edit",
    ),
    path(
        "<ulid:team_id>/action/",
        views.TeamActionApi.as_view(),
        name="team_action",
    ),
    path(
        "<ulid:team_id>/",
        views.TeamDetailApi.as_view(),
        name="team_detail",
    ),
    path(
        "add/",
        views.TeamCreateApi.as_view(),
        name="team_add",
    ),
    path(
        "",
        views.TeamListApi.as_view(),
        name="team_list",
    ),
]


""" API endpoints for select2 dropdowns """
select_urls = [
    path(
        "materials",
        select_views.MaterialSelectAPIView.as_view(),
        name="select_materials",
    ),
    path(
        "products", select_views.ProductSelectAPIView.as_view(), name="select_products"
    ),
    path(
        "resources",
        select_views.ResourceSelectAPIView.as_view(),
        name="select_resources",
    ),
    path(
        "units/appropriate",
        select_views.UnitMeasurementAppropriateSelectAPIView.as_view(),
        name="select_units_appropriate",
    ),
    path(
        "units",
        select_views.UnitMeasurementSelectAPIView.as_view(),
        name="select_units",
    ),
]


urlpatterns = [
    # masterdata
    path("materials/", include(material_urls)),
    path("products/", include(product_urls)),
    path("resources/", include(resource_urls)),
    path("teams/", include(team_urls)),
    # select
    path("select/", include(select_urls)),
]

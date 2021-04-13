from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters as common_converters, views as common_views
from apps.masterdata import views

register_converter(common_converters.ULIDConverter, "ulid")

app_name = "apps.masterdata"


unit_measurement_urls = [
    path(
        "<ulid:pk>/edit/",
        views.UnitMeasurementUpdateView.as_view(),
        name="unitmeasurement_edit",
    ),
    path(
        "<ulid:pk>/",
        views.UnitMeasurementDetailView.as_view(),
        name="unitmeasurement_detail",
    ),
    path(
        "add/",
        views.UnitMeasurementCreateView.as_view(),
        name="unitmeasurement_add",
    ),
    path(
        "",
        views.UnitMeasurementListView.as_view(),
        name="unitmeasurement_list",
    ),
]


urlpatterns = [
    path("masterdata/units/", include(unit_measurement_urls)),
    path("masterdata/", views.IndexView.as_view(), name="masterdata_index"),
]

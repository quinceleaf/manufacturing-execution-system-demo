from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters as common_converters
from apps.production import forms, models, views

register_converter(common_converters.ULIDConverter, "ulid")

app_name = "apps.production"


urlpatterns = [
    path("production/", views.IndexView.as_view(), name="production_index"),
]

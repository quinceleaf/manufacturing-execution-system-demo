from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters as common_converters
from apps.purchasing import views

register_converter(common_converters.ULIDConverter, "ulid")

app_name = "apps.purchasing"


urlpatterns = [
    path("purchasing/", views.IndexView.as_view(), name="purchasing_index"),
]

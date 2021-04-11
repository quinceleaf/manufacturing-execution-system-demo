from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters, views


register_converter(converters.ULIDConverter, "ulid")
app_name = "apps.common"

urlpatterns = [
    path(
        "settings/ui/sidebar-pin/",
        views.ui_toggle_sidebar_pin,
        name="settings_ui_toggle_sidebar_pin",
    ),
    path("", views.IndexView.as_view(), name="index"),
]

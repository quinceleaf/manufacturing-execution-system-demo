from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters as common_converters
from apps.users import views

register_converter(common_converters.ULIDConverter, "ulid")

app_name = "apps.users"

urlpatterns = [
    path("", views.IndexView.as_view(), name="users_index"),
]

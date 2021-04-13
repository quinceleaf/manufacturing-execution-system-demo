""" CaterChain.io URL Configuration """

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import debug_toolbar


urlpatterns = [
    # path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("api/v1/", include("apps.api.urls", namespace="api")),
    # path("select2/", include("django_select2.urls")),
    #
    path("users/", include("apps.users.urls", namespace="users")),
    path("", include("apps.common.urls", namespace="common")),
    #
    path("__debug__/", include(debug_toolbar.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "CaterChain.io Administration"
admin.site.site_title = "CaterChain.io Administration"
admin.site.index_title = "CaterChain.io Administration"

from django.contrib import admin

"""
Menu links for header
"""


def app_header_links(requests):

    links = [
        {"route": "apps.masterdata:masterdata_index", "label": "Master Data"},
        {"route": "apps.masterdata:masterdata_index", "label": "Placeholder"},
        {"route": "apps.masterdata:masterdata_index", "label": "Placeholder"},
        {"route": "apps.masterdata:masterdata_index", "label": "Placeholder"},
    ]
    return {"app_header_links": links}


def admin_app_list(requests):
    return {}
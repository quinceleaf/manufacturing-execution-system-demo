from django.contrib import admin

"""
Menu links for header
"""


def app_header_links(requests):

    links = []
    return {"app_header_links": links}


def admin_app_list(requests):
    return {}
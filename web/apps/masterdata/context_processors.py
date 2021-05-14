"""
Sidebar links for masterdata app
"""


def app_sidebar_links(requests):

    if requests.resolver_match.namespace == "masterdata":
        links = [
            {"route": "apps.masterdata:product_list", "label": "Products"},
            {
                "route": "apps.masterdata:billofmaterials_list",
                "label": "Bills of Materials",
            },
            {"route": "apps.masterdata:material_list", "label": "Materials"},
            {"route": "apps.masterdata:team_list", "label": "Teams"},
            {"route": "apps.masterdata:resource_list", "label": "Resources"},
            {
                "route": "apps.masterdata:unitmeasurement_list",
                "label": "Units of Measurement",
            },
        ]
        utilities = [
            {
                "route": "apps.masterdata:utility_list",
                "label": "Bulk Operations",
            },
        ]
        return {
            "module_name": "Master Data",
            "app_sidebar_links": links,
            "app_sidebar_utilities": utilities,
        }
    return {}

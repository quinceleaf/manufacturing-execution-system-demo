from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter

from apps.common import converters as common_converters, views as common_views
from apps.masterdata import forms, views

register_converter(common_converters.ULIDConverter, "ulid")

app_name = "apps.masterdata"


WIZARD_FORMS = [
    ("lines", forms.BillOfMaterialsLineFormSet),
    ("procedure", forms.BillOfMaterialsProcedureForm),
    ("yields", forms.BillOfMaterialsYieldForm),
    ("resources", forms.BillOfMaterialsResourceFormSet),
    ("characteristics", forms.BillOfMaterialsCharacteristicsForm),
    ("notes", forms.BillOfMaterialsNoteForm),
]


bill_of_materials_urls = [
    path(
        "<ulid:pk>/team/<str:team>/",
        views.change_bill_of_materials_team,
        name="billofmaterials_change_team",
    ),
    path(
        "<ulid:pk>/scale/",
        views.BillOfMaterialsScaleView.as_view(),
        name="billofmaterials_scale",
    ),
    path(
        "<ulid:pk>/pdf/<str:view_type>/<str:report_type>/",
        views.export_bill_of_materials_as_pdf,
        name="billofmaterials_pdf",
    ),
    path(
        "<ulid:pk>/",
        views.BillOfMaterialsDetailView.as_view(),
        name="billofmaterials_detail",
    ),
    path(
        "",
        views.BillOfMaterialsFilterView.as_view(),
        name="billofmaterials_list",
    ),
    path(
        "wizard/<ulid:pk>/",
        views.BillOfMaterialsWizardCreateView.as_view(WIZARD_FORMS),
        name="billofmaterials_wizard",
    ),
]


element_urls = [
    path(
        "<ulid:pk>/characteristics/<str:language>/",
        views.BillOfMaterialsCharacteristicsCreateView.as_view(),
        name="billofmaterials_characteristics_add",
    ),
    path(
        "characteristics/<ulid:pk>/edit/",
        views.BillOfMaterialsCharacteristicsUpdateView.as_view(),
        name="billofmaterials_characteristics_edit",
    ),
    path(
        "<ulid:pk>/lines/edit/",
        views.BillOfMaterialsLineUpdateView.as_view(),
        name="billofmaterials_lines_edit",
    ),
    path(
        "<ulid:pk>/note/",
        views.BillOfMaterialsNoteCreateView.as_view(),
        name="billofmaterials_note_add",
    ),
    path(
        "note/<ulid:pk>/edit/",
        views.BillOfMaterialsNoteUpdateView.as_view(),
        name="billofmaterials_note_edit",
    ),
    path(
        "<ulid:pk>/procedure/<str:language>/",
        views.BillOfMaterialsProcedureCreateView.as_view(),
        name="billofmaterialsprocedure_add",
    ),
    path(
        "procedure/<ulid:pk>/edit/",
        views.BillOfMaterialsProcedureUpdateView.as_view(),
        name="billofmaterialsprocedure_edit",
    ),
    path(
        "<ulid:pk>/resources/edit/",
        views.BillOfMaterialsResourceUpdateView.as_view(),
        name="billofmaterials_resources_edit",
    ),
    path(
        "<ulid:pk>/yield/",
        views.BillOfMaterialsYieldCreateView.as_view(),
        name="billofmaterials_yield_add",
    ),
    path(
        "yield/<ulid:pk>/edit/",
        views.BillOfMaterialsYieldUpdateView.as_view(),
        name="billofmaterials_yield_edit",
    ),
]


material_urls = [
    # Material Costs
    path(
        "<ulid:pk>/cost/add/",
        views.MaterialCostCreateView.as_view(),
        name="materialcost_add",
    ),
    # Materials
    path(
        "valid-units/",
        views.load_material_valid_units,
        name="load_material_valid_units",
    ),
    path("<ulid:pk>/edit/", views.MaterialUpdateView.as_view(), name="material_edit"),
    path("<ulid:pk>/", views.MaterialDetailView.as_view(), name="material_detail"),
    path("add/bulk/", views.MaterialBulkCreateView.as_view(), name="material_add_bulk"),
    path("add/", views.MaterialCreateView.as_view(), name="material_add"),
    path(
        "",
        views.MaterialFilterView.as_view(),
        name="material_list",
    ),
]


product_urls = [
    path(
        "<ulid:pk>/status/<str:status>/",
        views.change_product_status,
        name="product_change_status",
    ),
    path(
        "<ulid:pk>/version/",
        views.generate_product_version,
        name="product_increment_version",
    ),
    path(
        "<ulid:pk>/characteristics/edit/",
        views.ProductCharacteristicsUpdateView.as_view(),
        name="product_characteristics_edit",
    ),
    path("<ulid:pk>/duplicate/", views.duplicate_product, name="product_duplicate"),
    path("<ulid:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("<ulid:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("add/bulk/", views.ProductBulkCreateView.as_view(), name="product_add_bulk"),
    path("add/", views.ProductCreateView.as_view(), name="product_add"),
    path("", views.ProductFilterView.as_view(), name="product_list"),
]


resource_urls = [
    path("<ulid:pk>/edit/", views.ResourceUpdateView.as_view(), name="resource_edit"),
    path("<ulid:pk>/", views.ResourceDetailView.as_view(), name="resource_detail"),
    path("add/bulk/", views.ResourceBulkCreateView.as_view(), name="resource_add_bulk"),
    path("add/", views.ResourceCreateView.as_view(), name="resource_add"),
    path("", views.ResourceFilterView.as_view(), name="resource_list"),
]


team_urls = [
    path("<ulid:pk>/edit/", views.TeamUpdateView.as_view(), name="team_edit"),
    path("<ulid:pk>/", views.TeamDetailView.as_view(), name="team_detail"),
    path("add/bulk/", views.TeamBulkCreateView.as_view(), name="team_add_bulk"),
    path("add/", views.TeamCreateView.as_view(), name="team_add"),
    path("", views.TeamFilterView.as_view(), name="team_list"),
]


unit_measurement_urls = [
    path(
        "<ulid:pk>/",
        views.UnitMeasurementDetailView.as_view(),
        name="unitmeasurement_detail",
    ),
    path(
        "",
        views.UnitMeasurementFilterView.as_view(),
        name="unitmeasurement_list",
    ),
]


utility_urls = [
    path(
        "bulk-editing/confirm",
        views.UtilityOfflineUpdateConfirmChangesView.as_view(),
        name="utility_offline_edit_confirm_changes",
    ),
    path(
        "bulk-editing/",
        views.UtilityOfflineUpdateView.as_view(),
        name="utility_offline_edit",
    ),
    path(
        "bulk-editing/characteristics/confirm",
        views.UtilityBulkUpdateCharacteristicsConfirmChangesView.as_view(),
        name="utility_bulk_edit_characteristics_confirm_changes",
    ),
    path(
        "bulk-editing/characteristics/",
        views.UtilityBulkUpdateCharacteristicsView.as_view(),
        name="utility_bulk_edit_characteristics",
    ),
    path("", views.UtilityListView.as_view(), name="utility_list"),
]


urlpatterns = [
    path("masterdata/billofmaterials/elements/", include(element_urls)),
    path("masterdata/billofmaterials/", include(bill_of_materials_urls)),
    path("masterdata/materials/", include(material_urls)),
    path("masterdata/products/", include(product_urls)),
    path("masterdata/resources/", include(resource_urls)),
    path("masterdata/teams/", include(team_urls)),
    path("masterdata/units/", include(unit_measurement_urls)),
    path("masterdata/utility/", include(utility_urls)),
    path("masterdata/", views.IndexView.as_view(), name="masterdata_index"),
]

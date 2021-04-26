from django.contrib import admin
from django.urls import path

from admin_auto_filters.filters import AutocompleteFilter
from django_fsm_log.admin import StateLogInline
from import_export.admin import ImportExportModelAdmin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from apps.core.admin import (
    admin_link,
    BaseAdminConfig,
    ImmutableAdminConfig,
    ItemAsMaterialFilter,
    ItemAsProductFilter,
    ManufacturerFilter,
    MaterialFilter,
    ProductFilter,
)
from apps.core.views import MaterialFilterSearchView, ProductFilterSearchView
from apps.core.models import ExportCsvMixin
from apps.masterdata import forms, models
from apps.production import models as production_models
from apps.purchasing import models as purchasing_models
from apps.purchasing.admin import VendorCatalogInline


"""
Admin for following models:

BillOfMaterials
BillOfMaterialsCharacteristics
BillOfMaterialsLine
BillOfMaterialsNote
BillOfMaterialsProcedure
BillOfMaterialsTree
BillOfMaterialsYields

Item
ItemCharacteristics
ItemCost
ItemConversion

Material (PROXY)
MaterialCharacteristics (PROXY)
MaterialCost (PROXY)
MaterialConversion (PROXY)

Product (PROXY)
ProductCharacteristics (PROXY)
ProductCost (PROXY)
ProductConversion (PROXY)

Resource
Team
Settings
"""

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsCharacteristicsInline(admin.TabularInline):
    model = models.BillOfMaterialsCharacteristics
    extra = 0


class BillOfMaterialsLineInline(admin.TabularInline):
    model = models.BillOfMaterialsLine
    extra = 0


class BillOfMaterialsProcedureInline(admin.TabularInline):
    model = models.BillOfMaterialsProcedure
    extra = 0


class BillOfMaterialsLineInline(admin.TabularInline):
    model = models.BillOfMaterialsResource
    extra = 0


class BillOfMaterialsYieldInline(admin.TabularInline):
    model = models.BillOfMaterialsYield
    extra = 0


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsAdminConfig(BaseAdminConfig):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = models.Product.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    autocomplete_fields = ["product", "team"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "product",
                    "state",
                    "version",
                )
            },
        ),
        (
            "Resources",
            {"fields": ("team",)},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    inlines = (
        BillOfMaterialsCharacteristicsInline,
        BillOfMaterialsLineInline,
        BillOfMaterialsProcedureInline,
        BillOfMaterialsYieldInline,
        StateLogInline,
    )
    list_display = ("__str__", "version", "state")
    list_filter = ("state", "team", ProductFilter)
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ["product__name"]


@admin.register(models.BillOfMaterials)
class BillOfMaterialsAdmin(BillOfMaterialsAdminConfig):
    pass


class BillOfMaterialsCharacteristicsAdminConfig(BaseAdminConfig):
    autocomplete_fields = ["bill_of_materials"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                )
            },
        ),
        (
            "Production",
            {
                "fields": (
                    "leadtime",
                    "temperature_preparation",
                    "temperature_storage",
                    "temperature_service",
                    "note_production",
                )
            },
        ),
        (
            "Labor",
            {
                "fields": (
                    "total_active_time",
                    "total_inactive_time",
                    "staff_count",
                    "note_labor",
                )
            },
        ),
    )
    list_display = ("__str__", "bill_of_materials")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("bill_of_materials__product__name",)
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsCharacteristics)
class BillOfMaterialsCharacteristicsAdmin(BillOfMaterialsCharacteristicsAdminConfig):
    pass


class BillOfMaterialsCostAdminConfig(ImmutableAdminConfig):

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                )
            },
        ),
        (
            "Costs",
            {
                "fields": (
                    "total_cost",
                    "input_cost_oldest",
                    "input_cost_latest",
                )
            },
        ),
        (
            "Cost Table",
            {"fields": ("cost_table",)},
        ),
    ) + ImmutableAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = [
        "bill_of_materials",
        "cost_table",
        "input_cost_latest",
        "input_cost_oldest",
        "total_cost",
        "version",
    ] + ImmutableAdminConfig.readonly_fields
    search_fields = [
        "bill_of_materials__product__name",
    ]
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsCost)
class BillOfMaterialsCostAdmin(BillOfMaterialsCostAdminConfig):
    pass


class BillOfMaterialsLineAdminConfig(BaseAdminConfig):
    def bom_state(self, obj):
        return obj.bill_of_materials.get_state_display()

    bom_state.short_description = "State"

    autocomplete_fields = ["bill_of_materials", "unit"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                )
            },
        ),
        (
            "Line",
            {
                "fields": (
                    "sequence",
                    "quantity",
                    "unit",
                    "item",
                    "note",
                )
            },
        ),
        (
            "Standardized",
            {
                "fields": (
                    "quantity_standard",
                    "unit_standard",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials", "bom_state")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = [
        "version",
        "quantity_standard",
        "unit_standard",
    ] + BaseAdminConfig.readonly_fields
    search_fields = ["item__name", "bill_of_materials__product__name"]
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsLine)
class BillOfMaterialsLineAdmin(BillOfMaterialsLineAdminConfig):
    pass


class BillOfMaterialsNoteAdminConfig(BaseAdminConfig):
    def bom_state(self, obj):
        return obj.bill_of_materials.get_state_display()

    bom_state.short_description = "State"

    autocomplete_fields = [
        "bill_of_materials",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                    "note",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials", "bom_state")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("bill_of_materials__name",)
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsNote)
class BillOfMaterialsNoteAdmin(BillOfMaterialsNoteAdminConfig):
    pass


class BillOfMaterialsProcedureAdminConfig(BaseAdminConfig):
    def bom_state(self, obj):
        return obj.bill_of_materials.get_state_display()

    bom_state.short_description = "State"
    autocomplete_fields = ["bill_of_materials"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                )
            },
        ),
        (
            "Procedure",
            {
                "fields": (
                    "procedure",
                    "language",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials", "bom_state")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("bill_of_materials__name",)
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsProcedure)
class BillOfMaterialsProcedureAdmin(BillOfMaterialsProcedureAdminConfig):
    pass


class BillOfMaterialsResourceAdminConfig(BaseAdminConfig):
    def bom_state(self, obj):
        return obj.bill_of_materials.get_state_display()

    bom_state.short_description = "State"

    def resource_unit(self, obj):
        return obj.resource.resource_unit

    resource_unit.short_description = "Unit"

    autocomplete_fields = ["bill_of_materials", "resource"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                )
            },
        ),
        (
            "Resource",
            {
                "fields": (
                    "resource",
                    "sequence",
                    "capacity_required",
                    "changeover_required",
                    "note",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials", "bom_state")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = [
        "version",
    ] + BaseAdminConfig.readonly_fields
    search_fields = ["item", "bill_of_materials"]
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsResource)
class BillOfMaterialsResourceAdmin(BillOfMaterialsResourceAdminConfig):
    pass


@admin.register(models.BillOfMaterialsTree)
class BillOfMaterialsTreeAdmin(TreeAdmin):
    form = movenodeform_factory(models.BillOfMaterialsTree)
    list_filter = ("depth",)


class BillOfMaterialsYieldAdminConfig(BaseAdminConfig):
    def bom_state(self, obj):
        return obj.bill_of_materials.get_state_display()

    bom_state.short_description = "State"
    autocomplete_fields = ["bill_of_materials"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "bill_of_materials",
                    "version",
                    "yield_noun",
                )
            },
        ),
        (
            "Weight",
            {
                "fields": (
                    "quantity_weight",
                    "unit_weight",
                )
            },
        ),
        (
            "Volume",
            {
                "fields": (
                    "quantity_volume",
                    "unit_volume",
                )
            },
        ),
        (
            "Each",
            {
                "fields": (
                    "quantity_each",
                    "note_each",
                    "unit_each",
                )
            },
        ),
        (
            "Scaling",
            {
                "fields": (
                    "scale_multiple_smallest",
                    "scale_multiple_largest",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "bill_of_materials", "bom_state")
    list_display_links = ("__str__", "bill_of_materials")
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("bill_of_materials__product__name",)
    sortable_by = (
        "__str__",
        "bill_of_materials",
    )


@admin.register(models.BillOfMaterialsYield)
class BillOfMaterialsYieldAdmin(BillOfMaterialsYieldAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ITEM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ItemAdminConfig(BaseAdminConfig, ExportCsvMixin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "unit_type",
                )
            },
        ),
        (
            "Tags",
            {"fields": ("tags",)},
        ),
        (
            "Audit & Compliance",
            {
                "fields": (
                    "version",
                    "preserve",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__",)
    list_display_links = ("__str__",)
    list_filter = ("category",)
    readonly_fields = [
        "preserve",
        "version",
    ] + BaseAdminConfig.readonly_fields
    search_fields = ["name"]


@admin.register(models.Item)
class ItemAdmin(ItemAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class MaterialAdminConfig(BaseAdminConfig, ExportCsvMixin):
    def input_count(self, obj):
        return obj.inputs.count()

    input_count.short_description = "Input Count"

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Choices for model Material (the differentiating criteria between
        Material and its proxy model Product) should be limited to only material-appropriate options
        """
        if db_field.name == "category":
            kwargs["choices"] = [
                ("RAW", "Raw Food"),
                ("PREPARED", "Prepared Food"),
                ("SERVICE", "Service"),
                ("MRO", "Maintenance/Operating Supplies"),
                ("PACKAGING", "Packaging/Disposable"),
                ("OTHER", "Other/Misc"),
            ]
        return super(MaterialAdminConfig, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )

    actions = ["export_as_csv"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "unit_type",
                    "state",
                )
            },
        ),
        (
            "Tags",
            {"fields": ("tags",)},
        ),
        (
            "Audit & Compliance",
            {
                "fields": (
                    "version",
                    "preserve",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__", "input_count")
    list_display_links = ("__str__", "input_count")
    list_filter = ("category",)
    readonly_fields = [
        "preserve",
        "version",
    ] + BaseAdminConfig.readonly_fields
    search_fields = ["name"]


@admin.register(models.Material)
class MaterialAdmin(MaterialAdminConfig):
    pass


@admin.register(models.MaterialCharacteristics)
class MaterialCharacteristicsAdmin(BaseAdminConfig):
    autocomplete_fields = ["item"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item",
                    "state",
                    "version",
                )
            },
        ),
        (
            "Allergens Evaluation",
            {
                "fields": (
                    "contains_crustacea",
                    "contains_dairy",
                    "contains_egg",
                    "contains_fish",
                    "contains_peanut",
                    "contains_sesame",
                    "contains_soy",
                    "contains_treenut",
                    "contains_wheat",
                )
            },
        ),
        (
            "Religious/Dietary Preference Evaluation",
            {
                "fields": (
                    "contains_alcohol",
                    "contains_gelatin",
                    "contains_honey",
                    "contains_meat",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_filter = (ItemAsMaterialFilter,)
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("item__name",)


@admin.register(models.MaterialConversion)
class MaterialConversionAdmin(BaseAdminConfig):
    autocomplete_fields = ["item"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item",
                    "version",
                )
            },
        ),
        (
            "Allowed Units",
            {
                "fields": (
                    "allowed_weight",
                    "allowed_volume",
                    "allowed_each",
                )
            },
        ),
        (
            "Conversion Ratios",
            {
                "fields": (
                    "ratio_weight_to_volume",
                    "ratio_weight_to_each",
                    "ratio_volume_to_each",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_filter = (ItemAsMaterialFilter,)
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields


@admin.register(models.MaterialCost)
class MaterialCostAdmin(ImmutableAdminConfig):
    list_filter = (ItemAsMaterialFilter,)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ProductAdminConfig(BaseAdminConfig, ExportCsvMixin):
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Choices for proxy model Product (the differentiating criteria between
        Product and Material) should be limited to only product-appropriate options
        """
        if db_field.name == "category":
            kwargs["choices"] = [
                ("WIP", "Work-in-Progress"),
                ("FINISHED", "Finished Product"),
            ]
        return super(ProductAdminConfig, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )

    actions = ["export_as_csv"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "unit_type",
                    "state",
                )
            },
        ),
        (
            "Tags",
            {"fields": ("tags",)},
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
        (
            "Audit & Compliance",
            {
                "fields": (
                    "version",
                    "preserve",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__",)
    list_display_links = ("__str__",)
    list_filter = (
        "category",
        "state",
    )
    readonly_fields = [
        "preserve",
        "version",
    ] + BaseAdminConfig.readonly_fields
    search_fields = ["name"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "product_filter/",
                self.admin_site.admin_view(
                    ProductFilterSearchView.as_view(model_admin=self)
                ),
                name="product_filter",
            ),
        ]
        return custom_urls + urls


@admin.register(models.Product)
class ProductAdmin(ProductAdminConfig):
    pass


@admin.register(models.ProductCharacteristics)
class ProductCharacteristicsAdmin(BaseAdminConfig):
    autocomplete_fields = ["item"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item",
                    "state",
                    "version",
                )
            },
        ),
        (
            "Pricing",
            {"fields": ("unit_price",)},
        ),
        (
            "Customer Information",
            {
                "fields": (
                    "description",
                    "upc_code",
                    "shelf_life",
                )
            },
        ),
        (
            "Allergens Evaluation",
            {
                "fields": (
                    "contains_crustacea",
                    "contains_dairy",
                    "contains_egg",
                    "contains_fish",
                    "contains_peanut",
                    "contains_sesame",
                    "contains_soy",
                    "contains_treenut",
                    "contains_wheat",
                )
            },
        ),
        (
            "Religious/Dietary Preference Evaluation",
            {
                "fields": (
                    "contains_alcohol",
                    "contains_gelatin",
                    "contains_honey",
                    "contains_meat",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_filter = (ItemAsProductFilter,)
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields
    search_fields = ("item__name",)


@admin.register(models.ProductConversion)
class ProductConversionAdmin(BaseAdminConfig):
    autocomplete_fields = ["item"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "item",
                    "version",
                )
            },
        ),
        (
            "Allowed Units",
            {
                "fields": (
                    "allowed_weight",
                    "allowed_volume",
                    "allowed_each",
                )
            },
        ),
        (
            "Conversion Ratios",
            {
                "fields": (
                    "ratio_weight_to_volume",
                    "ratio_weight_to_each",
                    "ratio_volume_to_each",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_filter = (ItemAsProductFilter,)
    readonly_fields = ["version"] + BaseAdminConfig.readonly_fields


@admin.register(models.ProductCost)
class ProductCostAdmin(ImmutableAdminConfig):
    list_filter = (ItemAsProductFilter,)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# RESOURCE
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Resource)
class ResourceAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {"fields": ("name", "capacity", "unit", "resource_type", "stage")},
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = (
        "__str__",
        "capacity",
        "unit",
    )
    search_fields = ("name",)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Settings)
class SettingsAdmin(BaseAdminConfig):
    autocomplete_fields = ["default_unit_weight", "default_unit_volume"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "default_unit_weight",
                    "default_unit_volume",
                    "default_unit_system_weight",
                    "default_unit_system_volume",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    form = forms.SettingsForm


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Team)
class TeamAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    search_fields = ("name",)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# UNIT MEASUREMENT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.UnitMeasurement)
class UnitMeasurementAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "symbol",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "unit_system",
                    "unit_type",
                    "display_quantity_smallest",
                    "display_quantity_largest",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = (
        "__str__",
        "symbol",
        "unit_system",
        "unit_type",
    )
    list_filter = (
        "unit_system",
        "unit_type",
    )

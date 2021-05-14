from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from admin_auto_filters.filters import AutocompleteFilter
from django_fsm_log.admin import StateLogInline

from apps.common import models
from apps.masterdata import models as masterdata_models

"""
Admin for:
common admin mixins
UnitMeasurement
"""

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse("admin:{}_{}_change".format(app_label, model_name), args=(obj.pk,))


def admin_link(attr, short_description, empty_description="-"):
    """Decorator used for rendering a link to a related model in
    the admin detail page.

    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.

    The wrapped method receives the related object and should
    return the link text.

    Usage:
        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """

    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html('<a href="{}">{}</a>', url, func(self, related_obj))

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


class BaseAdminConfig(admin.ModelAdmin, models.ExportCsvMixin):

    readonly_fieldsets = (
        (
            "ID/Timestamps",
            {"classes": ("collapse",), "fields": ("id", "created_at", "updated_at")},
        ),
    )

    actions = ["export_as_csv"]
    list_display = ("__str__",)
    list_display_links = ("__str__",)
    list_per_page = 25
    readonly_fields = ["id", "created_at", "updated_at"]
    search_fields = ("__str__",)
    sortable_by = ("__str__",)


class ImmutableAdminConfig(admin.ModelAdmin, models.ExportCsvMixin):

    readonly_fieldsets = (
        ("ID/Timestamps", {"classes": ("collapse",), "fields": ("id", "created_at")}),
    )

    actions = ["export_as_csv"]
    list_display = ("__str__",)
    list_display_links = ("__str__",)
    list_per_page = 25
    readonly_fields = ["id", "created_at"]
    search_fields = ("__str__",)
    sortable_by = ("__str__",)


class ItemAsMaterialFilter(AutocompleteFilter):
    title = "Material"
    field_name = "item"

    # def get_autocomplete_url(self, request, model_admin):
    #     return reverse("admin:material_filter")


class ItemAsProductFilter(AutocompleteFilter):
    title = "Product"
    field_name = "item"

    # def get_autocomplete_url(self, request, model_admin):
    #     return reverse("admin:product_filter")


class ManufacturerFilter(AutocompleteFilter):
    title = "Manufacturer"
    field_name = "manufacturer"

    # def get_autocomplete_url(self, request, model_admin):
    #     return reverse("admin:manufacturer_filter")


class MaterialFilter(AutocompleteFilter):
    title = "Material"
    field_name = "item"


class MaterialasItemFilter(AutocompleteFilter):
    title = "Material"
    field_name = "item"

    # def get_autocomplete_url(self, request, model_admin):
    #     return reverse("admin:material_filter")

    # def get_queryset(self):
    #     MATERIAL_VALID_CATEGORIES = [
    #         "RAW",
    #         "PREPARED",
    #         "SERVICE",
    #         "MRO",
    #         "PACKAGING",
    #         "OTHER",
    #     ]
    #     queryset = masterdata_models.Item.objects.filter(
    #         category__in=MATERIAL_VALID_CATEGORIES
    #     )
    #     return queryset


class ProductFilter(AutocompleteFilter):
    title = "Product"
    field_name = "product"


class FinishedProductFilter(AutocompleteFilter):
    title = "Product"
    field_name = "item"

    # def get_queryset(self):
    #     queryset = masterdata_models.Product.objects.filter(category="FINISHED")
    #     return queryset


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TAG
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Tag)
class TagAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {"fields": ("name",)},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    search_fields = ("name",)
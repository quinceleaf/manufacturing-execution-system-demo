# ––– DJANGO IMPORTS
from django.contrib import admin
from django.contrib.auth.admin import AdminPasswordChangeForm, UserAdmin
from django.utils.html import mark_safe


# ––– APPLICATION IMPORTS
from apps.users import forms, models
from apps.common.admin import admin_link, BaseAdminConfig


"""
Admin for following models:

Domain
Organization
SiteSettings
User
Settings
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ADD-ONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UserInline(admin.TabularInline):
    model = models.User


class SettingsInline(admin.TabularInline):
    model = models.Settings


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# DOMAINS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "domain",
                    "organization",
                )
            },
        ),
        (
            "ID/Timestamps",
            {"classes": ("collapse",), "fields": ("id",)},
        ),
    )
    list_display = ("__str__",)
    list_per_page = 25
    readonly_fields = ["id"]
    search_fields = ("__str__",)
    sortable_by = ("__str__",)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SITE SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.SiteSettings)
class SiteSettingsAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {"fields": ()},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    form = forms.SiteSettingsForm
    list_display = ("__str__",)
    readonly_fields = BaseAdminConfig.readonly_fields


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ORGANIZATION
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Organization)
# class OrganizationAdmin(OrganizationAdminMixin, BaseAdminConfig):
class OrganizationAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {"fields": ("name", "subscription_level", "state", "notes")},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = ("__str__",)
    readonly_fields = BaseAdminConfig.readonly_fields
    search_fields = ("user",)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# USER
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.User)
class UserAdmin(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "is_active",
                )
            },
        ),
        (
            "Last Login",
            {"fields": ("last_login",)},
        ),
        (
            "Groups & Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    filter_horizontal = ["groups", "user_permissions"]
    inlines = (SettingsInline,)
    readonly_fields = ["id", "created_at", "last_login", "updated_at"]


@admin.register(models.Settings)
class SettingsAdmin(BaseAdminConfig):
    def avatar_image(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="150" height="150" />')

    search_fields = ("user",)
    autocomplete_fields = [
        "user",
    ]
    fieldsets = (
        (
            None,
            {"fields": ("user",)},
        ),
        (
            "Avatar",
            {"fields": ("avatar", "avatar_image")},
        ),
    ) + BaseAdminConfig.readonly_fieldsets
    list_display = (
        "__str__",
        "avatar_image",
    )
    readonly_fields = [
        "avatar_image",
    ] + BaseAdminConfig.readonly_fields

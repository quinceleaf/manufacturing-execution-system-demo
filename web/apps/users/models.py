# ––– DJANGO IMPORTS
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _


# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by


# ––– PROJECT IMPORTS
from apps.common import models as core_models


# ––– PARAMETERS


# ––– MODELS


class Organization(core_models.AbstractBaseModel):

    STATE_CHOICES = (
        ("CURRENT", "Current"),
        ("NAN", "No Approval Necessary"),
        ("LAPSED", "Lapsed"),
    )

    SUBSCRIPTION_LEVEL_CHOICES = (
        ("FREE", "Free"),
        ("TRIAL", "Trial"),
        ("PRO", "Professional"),
    )

    name = models.CharField("Name", max_length=96, null=False)
    notes = models.TextField("Notes", null=True, blank=True)
    state = FSMField(
        default="CURRENT",
        verbose_name="Status",
        choices=STATE_CHOICES,
        # protected=True,
    )
    subscription_level = models.CharField(
        "Subscription Level", max_length=24, default="FREE"
    )
    tenant_id = "id"

    def __str__(self):
        return str(self.name)

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # CURRENT - tenant is active and current with account
    # NO APPROVAL NEEDED - tenant exists outside of approval structure (admin/pro bono)
    # LAPSED - tenant is inactive or account is past due
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Users of tenants that are CURRENT can log in normally
    # Users of tenants that are NO APPROVAL NEEDED can log in normally
    # Users of tenants that are LAPSED can log in on a read-only basis

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="CURRENT",
        permission="app.change_tenant_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="NAN",
        permission="app.change_tenant_status",
    )
    def no_approval_needed(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="LAPSED",
        permission="app.change_tenant_status",
    )
    def lapsed(self, by=None):
        return

    class Meta:
        ordering = ["name"]
        permissions = [
            ("change_tenant_status", "Can change status of tenant"),
        ]


class Domain(core_models.AbstractBaseModel):
    """ Domain for organization """

    domain = models.CharField(max_length=36, null=False, blank=False)

    # organization = TenantOneToOneField(
    #     Organization,
    #     on_delete=models.CASCADE,
    #     related_name="requests",
    # )
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="requests",
    )

    def __str__(self):
        return f"Domain {domain} | organization {organization}"


class SiteSettings(core_models.AbstractBaseModel):
    """ Site settings """

    def __str__(self):
        return f"Site settings"

    class Meta:
        verbose_name_plural = "Site settings"


class User(PermissionsMixin, AbstractBaseUser, core_models.AbstractBaseModel):
    username_validator = UnicodeUsernameValidator()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    email = models.EmailField("Email address", blank=True)
    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=80, null=True, blank=True)
    username = models.CharField(
        "Username", max_length=255, unique=True, validators=[username_validator]
    )

    objects = UserManager()

    class Meta:
        ordering = [
            "last_name",
            "first_name",
        ]

    def __str__(self):
        return f"{self.username}"


class Settings(core_models.AbstractBaseModel):

    avatar = models.ImageField(
        upload_to="avatars",
        default="../static/img/avatars/default-user-avatar.png",
        null=True,
        blank=True,
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user} | settings"

    class Meta:
        verbose_name_plural = "Settings"


@receiver(post_save, sender=User)
def create_settings_on_user_creation(sender, created, instance, **kwargs):
    """
    Create Settings upon User instance creation
    """
    from apps.users.models import Settings

    if created:
        Settings(user=instance)


@receiver(post_save, sender=User)
def create_settings_on_initial_user_creation(sender, created, instance, **kwargs):
    """ Create settings for all relevant CaterChain project apps upon initial user creation """
    from django.apps import registry

    if User.objects.all().count() == 1:
        for app in settings.PROJECT_APPS:
            APPS_WITHOUT_SETTINGS = ["apps.common", "apps.api", "apps.users"]
            if app in APPS_WITHOUT_SETTINGS:
                continue
            app_label = app.split(".")[1]
            try:
                settings_model = registry.apps.get_model(app_label, "Settings")
            except LookupError:
                continue
            if settings_model.objects.all().count() == 0:
                settings_model.objects.create()
        return
    else:
        return

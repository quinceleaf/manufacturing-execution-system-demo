# ––– DJANGO IMPORTS
from django import forms
from django.forms import (
    BaseInlineFormSet,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
)

# ––– THIRD-PARTY IMPORTS
from django_select2 import forms as s2forms


# ––– APPLICATION IMPORTS
from apps.common.forms import BaseModelForm
from apps.users import models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# WIDGETS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FORMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UserForm(BaseModelForm):
    class Meta:
        model = models.User
        fields = ("username",)


class SiteSettingsForm(BaseModelForm):
    def clean(self):
        super().clean()
        """ Can only be single instance of settings per app, per tenant """
        if self.instance._state.adding and models.Settings.objects.exists():
            raise forms.ValidationError(
                "There can be only a single Settings instance for each module"
            )

    class Meta:
        model = models.SiteSettings
        fields = ()

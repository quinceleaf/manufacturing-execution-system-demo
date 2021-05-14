# ––– DJANGO IMPORTS
from django import forms


# –––THIRD-PARTY IMPORTS
from django_select2 import forms as s2forms


# ––– PROJECT IMPORTS
from apps.api import select_views
from apps.common import models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# WIDGETS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ItemWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.ItemSelectAPIView
    search_fields = ["name__icontains"]


class MaterialWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.MaterialSelectAPIView
    search_fields = ["name__icontains"]


class ProductWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.ProductSelectAPIView
    search_fields = ["name__icontains"]


class TeamWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.TeamSelectAPIView
    search_fields = ["name__icontains"]


class UnitMeasurementWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.UnitMeasurementSelectAPIView
    search_fields = ["name__icontains", "symbol__icontains"]


class UnitMeasurementWeightWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.UnitMeasurementWeightSelectAPIView
    search_fields = ["name__icontains", "symbol__icontains"]
    attrs = (
        {
            "data-placeholder": "Select ...",
            "data-minimum-input-length": 1,
            "class": "django-select2",
        },
    )


class UnitMeasurementVolumeWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.UnitMeasurementVolumeSelectAPIView
    search_fields = ["name__icontains", "symbol__icontains"]


class UnitMeasurementEachWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.UnitMeasurementEachSelectAPIView
    search_fields = ["name__icontains", "symbol__icontains"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FORMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(BaseModelForm, self).__init__(*args, **kwargs)


class TagForm(BaseModelForm):
    def clean_name(self):
        """ Name should be unique """
        objs = models.Tag.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Tag with same name already exists")
        return name

    class Meta:
        model = models.Tag
        fields = ("name",)


class TagBulkForm(BaseModelForm):

    name_bulk = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "name"}),
    )

    def clean_name(self):
        """ Name should be unique """
        objs = models.Tag.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Tag with same name already exists")
        return name

    class Meta:
        model = models.Tag
        fields = ("name_bulk",)

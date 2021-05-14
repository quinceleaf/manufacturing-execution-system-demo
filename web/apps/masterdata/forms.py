from django import forms

from django.forms import (
    BaseInlineFormSet,
    formset_factory,
    inlineformset_factory,
    modelformset_factory,
)
from django.db.models import Q

from django_select2 import forms as s2forms

from apps.api import select_views
from apps.common.forms import BaseModelForm
from apps.masterdata import models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# WIDGETS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsLineChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.item.name}"


class BillOfMaterialsLineWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.BillOfMaterialsLineSelectAPIView
    search_fields = ["item__icontains"]


class MaterialWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.MaterialSelectAPIView
    search_fields = ["name__icontains"]


class ResourceWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.ResourceSelectAPIView
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


class UnitMeasurementAnnotatedWidget(s2forms.ModelSelect2Widget):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # if value:
        option["attrs"]["data-unittype"] = value.instance.unit_type
        return option


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FORMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class BillOfMaterialsCharacteristicsForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(BillOfMaterialsCharacteristicsForm, self).__init__(*args, **kwargs)
        """ Don't make user pick from dropdown if only single option """
        if models.Team.objects.count() == 1:
            self.fields["team"].initial = models.Team.objects.get()

        """ Provide placeholders for simple choice-based dropdowns """
        self.fields["temperature_preparation"].empty_label = "Select..."
        self.fields["temperature_storage"].empty_label = "Select..."
        self.fields["temperature_service"].empty_label = "Select..."

    team = forms.ModelChoiceField(
        queryset=models.Team.objects.all(),
        required=True,
        label="Team",
    )

    note_labor = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "id": "notes-1",
                "class": "prose",
            }
        ),
    )

    note_production = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "id": "notes-2",
                "class": "prose",
            }
        ),
    )

    class Meta:
        model = models.BillOfMaterialsCharacteristics
        fields = (
            "team",
            "leadtime",
            "temperature_preparation",
            "temperature_storage",
            "temperature_service",
            "note_production",
            "total_active_time",
            "total_inactive_time",
            "staff_count",
            "note_labor",
        )
        widgets = {"team": TeamWidget}


class BillOfMaterialsLineForm(BaseModelForm):

    unit = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.all(),
        required=False,
        label="Unit",
    )

    # unit = ModelChoiceFieldWithData(
    #     queryset=models.UnitMeasurement.objects.all(),
    #     required=False,
    #     label="Unit",
    #     # additional_data=("unit_type",),
    # )

    item = forms.ModelChoiceField(
        queryset=models.Item.objects.all(),
        required=False,
        label="Material",
    )

    class Meta:
        model = models.BillOfMaterialsLine
        fields = ("sequence", "quantity", "unit", "item", "note")
        widgets = {
            "item": MaterialWidget,
            "unit": UnitMeasurementAnnotatedWidget,
        }
        # "unit": UnitMeasurementWidget}


BillOfMaterialsLineFormSet = inlineformset_factory(
    parent_model=models.BillOfMaterials,
    model=models.BillOfMaterialsLine,
    form=BillOfMaterialsLineForm,
    fields=[
        "sequence",
        "quantity",
        "unit",
        "item",
        "note",
    ],
    widgets={"item": MaterialWidget, "unit": UnitMeasurementAnnotatedWidget},
    extra=0,
    can_delete=True,
)


class BillOfMaterialsNoteForm(BaseModelForm):

    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "note"}),
    )

    class Meta:
        model = models.BillOfMaterialsNote
        fields = ("note",)


class BillOfMaterialsProcedureForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language", None)
        super(BillOfMaterialsProcedureForm, self).__init__(*args, **kwargs)
        """ Provide placeholders for simple choice-based dropdowns """
        if self.language:
            self.fields["language"].initial = self.language
            self.fields["language"].widget.attrs["disabled"] = True

    procedure = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "id": "editor",
            },
        ),
    )

    class Meta:
        model = models.BillOfMaterialsProcedure
        fields = ("language", "procedure")


class BillOfMaterialsResourceForm(BaseModelForm):

    resource = forms.ModelChoiceField(
        queryset=models.Resource.objects.all(),
        required=False,
        label="Resource",
    )

    class Meta:
        model = models.BillOfMaterialsResource
        fields = ("sequence", "capacity_required", "resource", "note")
        widgets = {
            "resource": ResourceWidget,
        }


BillOfMaterialsResourceFormSet = inlineformset_factory(
    parent_model=models.BillOfMaterials,
    model=models.BillOfMaterialsResource,
    form=BillOfMaterialsResourceForm,
    fields=[
        "sequence",
        "capacity_required",
        "resource",
        "note",
    ],
    extra=0,
    can_delete=True,
)


class BillOfMaterialsScaleForm(BaseModelForm):
    """ Form for scaling modal within BillOfMaterials Detail """

    def __init__(self, *args, **kwargs):
        self.bill_of_materials = kwargs.pop("bill_of_materials", None)
        super(BillOfMaterialsScaleForm, self).__init__(*args, **kwargs)

        """ Set initial value for desired yield to base yield of batch """
        if self.bill_of_materials and self.bill_of_materials.yields.unit_weight:
            self.fields[
                "yield_quantity_weight"
            ].initial = self.bill_of_materials.yields.quantity_weight
            self.fields[
                "yield_unit_weight"
            ].initial = self.bill_of_materials.yields.unit_weight_id
            self.fields["yield_choice"].initial = "WEIGHT"
        if self.bill_of_materials and self.bill_of_materials.yields.unit_volume:
            self.fields[
                "yield_quantity_volume"
            ].initial = self.bill_of_materials.yields.quantity_volume
            self.fields[
                "yield_unit_volume"
            ].initial = self.bill_of_materials.yields.unit_volume_id
            self.fields["yield_choice"].initial = "VOLUME"
        if self.bill_of_materials and self.bill_of_materials.yields.unit_each:
            self.fields[
                "yield_quantity_each"
            ].initial = self.bill_of_materials.yields.quantity_each
            self.fields[
                "yield_unit_each"
            ].initial = self.bill_of_materials.yields.unit_each_id
            self.fields["yield_choice"].initial = "EACH"

        """ Sets option for yield_unit_each and disables """
        self.fields["yield_unit_each"].initial = models.UnitMeasurement.objects.get(
            symbol="ea"
        )
        self.fields["yield_unit_each"].widget.attrs["disabled"] = True

        """ Limit lines to those within BOM """
        if self.bill_of_materials:
            self.fields[
                "limit_line"
            ].queryset = models.BillOfMaterialsLine.objects.filter(
                bill_of_materials=self.bill_of_materials
            )
            self.fields[
                "limit_line"
            ].widget.queryset = models.BillOfMaterialsLine.objects.filter(
                bill_of_materials=self.bill_of_materials
            )

    scale_type = forms.ChoiceField(
        choices=[("WEIGHT", "Weight"), ("VOLUME", "Volume"), ("EACH", "Each")],
        required=True,
        label="Scale Type",
        widget=forms.RadioSelect,
    )

    """ Scale by desired yield """
    yield_choice = forms.ChoiceField(
        choices=[("WEIGHT", "Weight"), ("VOLUME", "Volume"), ("EACH", "Each")],
        required=True,
        label="Yield Choice",
        widget=forms.RadioSelect,
    )

    yield_quantity_weight = forms.DecimalField(
        label="Quantity", min_value=0.010, decimal_places=3, initial=1.000
    )

    yield_unit_weight = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="WEIGHT"),
        required=False,
        label="Unit",
        empty_label="Select...",
    )

    yield_quantity_volume = forms.DecimalField(
        label="Quantity", min_value=0.010, decimal_places=3, initial=1.000
    )

    yield_unit_volume = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="VOLUME"),
        required=False,
        label="Unit",
        empty_label="Select...",
    )

    yield_quantity_each = forms.DecimalField(
        label="Quantity", min_value=0.010, decimal_places=3, initial=1.000
    )

    yield_unit_each = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="EACH"),
        required=False,
        label="Unit",
        empty_label="Select...",
    )

    """ Scale by multiple """
    multiple_scaling_factor = forms.DecimalField(
        label="Scale Batch by", min_value=0.010, decimal_places=3, initial=1.000
    )

    """ Scale by limiting line """
    limit_quantity = forms.DecimalField(
        label="Quantity", min_value=0.010, decimal_places=3, initial=1.000
    )

    limit_unit = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.all(),
        required=False,
        label="Unit",
        empty_label="Select...",
    )

    limit_line = BillOfMaterialsLineChoiceField(
        queryset=models.BillOfMaterialsLine.objects.all(),
        required=False,
        label="Material Line",
        empty_label="Select...",
    )

    class Meta:
        model = models.BillOfMaterials
        fields = (
            "scale_type",
            "yield_choice",
            "yield_quantity_weight",
            "yield_unit_weight",
            "yield_quantity_volume",
            "yield_unit_volume",
            "yield_quantity_each",
            "yield_unit_each",
            "multiple_scaling_factor",
            "limit_quantity",
            "limit_unit",
            "limit_line",
        )
        widgets = {
            "yield_unit_weight": UnitMeasurementWeightWidget,
            "yield_unit_volume": UnitMeasurementVolumeWidget,
            "yield_unit_each": UnitMeasurementEachWidget,
            "limit_unit": UnitMeasurementAnnotatedWidget,
            "limit_line": BillOfMaterialsLineWidget,
        }


class BillOfMaterialsYieldForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(BillOfMaterialsYieldForm, self).__init__(*args, **kwargs)
        """ Provide placeholders for simple choice-based dropdowns """
        self.fields["unit_weight"].empty_label = "Select..."
        self.fields["unit_volume"].empty_label = "Select..."
        self.fields["unit_each"].empty_label = "Select..."

        """ Prepopulate with defaults """
        self.fields[
            "scale_multiple_smallest"
        ].initial = self.Meta.model._meta.get_field(
            "scale_multiple_smallest"
        ).get_default()
        self.fields["scale_multiple_largest"].initial = self.Meta.model._meta.get_field(
            "scale_multiple_largest"
        ).get_default()

    unit_each = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.all(),
        # queryset=models.UnitMeasurement.objects.filter(unit_type="EACH"),
        required=False,
        label="Unit (Each)",
    )

    unit_volume = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="VOLUME"),
        required=False,
        label="Unit (Volume)",
    )

    unit_weight = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="WEIGHT"),
        required=False,
        label="Unit (Weight)",
    )

    def clean(self):
        """ If quantity_each and unit_each, must also specify note_each """
        if (
            self.cleaned_data["quantity_each"] and self.cleaned_data["unit_each"]
        ) and not self.cleaned_data["note_each"]:
            raise forms.ValidationError(
                "To specify an each yield, must provide a quantity, a unit and a note indicating what each references"
            )

        """ Must specify at least one yield with both quantity and unit """
        if not any(
            [
                self.cleaned_data["quantity_weight"]
                and self.cleaned_data["unit_weight"],
                self.cleaned_data["quantity_volume"]
                and self.cleaned_data["unit_volume"],
                self.cleaned_data["quantity_each"]
                and self.cleaned_data["unit_each"]
                and self.cleaned_data["note_each"],
            ]
        ):
            raise forms.ValidationError(
                "Must specify at least one yield with both quantity and unit"
            )

    class Meta:
        model = models.BillOfMaterialsYield
        fields = (
            "quantity_weight",
            "unit_weight",
            "quantity_volume",
            "unit_volume",
            "quantity_each",
            "unit_each",
            "note_each",
            "scale_multiple_smallest",
            "scale_multiple_largest",
        )
        widgets = {
            "material": MaterialWidget,
            "unit_weight": UnitMeasurementWeightWidget,
            "unit_volume": UnitMeasurementVolumeWidget,
            "unit_each": UnitMeasurementEachWidget,
        }


class MaterialForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        VALID_CATEGORY_CHOICES = ["RAW", "PREPARED", "MRO", "PACKAGING", "OTHER"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in VALID_CATEGORY_CHOICES
        ]

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_name(self):
        """ Name should be unique """
        name = self.cleaned_data["name"]

        objs = models.Material.objects.filter(name=name)
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)
        if objs.exists():
            raise forms.ValidationError("Material with same name already exists")
        return name

    class Meta:
        model = models.Material
        fields = (
            "name",
            "category",
            "unit_type",
            "is_available",
            "notes",
        )


class MaterialBulkForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialBulkForm, self).__init__(*args, **kwargs)
        valid_choices = ["RAW", "PREPARED", "MRO", "PACKAGING", "OTHER"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in valid_choices
        ]

    name_bulk = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "name"}),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_name_bulk(self):
        """ Name should be unique """
        name_bulk = self.cleaned_data["name_bulk"]
        name_list = name_bulk.split("\r\n")

        for name in name_list:
            objs = models.Material.objects.filter(name=name)
            if self.instance.id:
                objs = objs.exclude(id=self.instance.id)
            if objs.exists():
                raise forms.ValidationError("Material with same name already exists")

        return name_bulk

    class Meta:
        model = models.Material
        fields = (
            "name_bulk",
            "category",
            "unit_type",
            "is_available",
            "notes",
        )


class MaterialCostForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        self.material = kwargs.pop("material", None)
        super(MaterialCostForm, self).__init__(*args, **kwargs)

        if self.material:
            self.fields["item"].initial = self.material
            self.fields["item"].widget.attrs["disabled"] = True

        self.fields["basis"].initial = "DIRECT"
        self.fields["basis"].widget.attrs["disabled"] = True

    item = forms.ModelChoiceField(
        queryset=models.Material.objects.all(),
        required=True,
        label="Material",
    )

    class Meta:
        model = models.MaterialCost
        fields = (
            "item",
            "basis",
            "unit_cost_weight",
            "unit_cost_volume",
            "unit_cost_each",
        )


class ProductForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        # Limit available category choices to those valid for Product
        VALID_CATEGORY_CHOICES = ["WIP", "FINISHED"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in VALID_CATEGORY_CHOICES
        ]

        # Initial unit type choice should be 'Each'
        self.fields["unit_type"].initial = "EACH"

    is_available = forms.BooleanField(
        required=False, label="Available to Sales", initial=True
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_category(self):
        """ Category must be valid: either WIP or FINISHED """
        VALID_CATEGORY_CHOICES = ["WIP", "FINISHED"]

        category = self.cleaned_data["category"]
        if category not in VALID_CATEGORY_CHOICES:
            raise forms.ValidationError("Category must be either 'WIP' or 'FINISHED'")
        return category

    def clean_name(self):
        """ Name must be unique """
        name = self.cleaned_data["name"]

        objs = models.Product.objects.filter(name=name)
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)
        if objs.exists():
            raise forms.ValidationError("Product with same name already exists")

        return name

    class Meta:
        model = models.Product
        fields = (
            "name",
            "category",
            "production_type",
            "unit_type",
            "is_available",
            "notes",
        )


class ProductBulkForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductBulkForm, self).__init__(*args, **kwargs)

        # Limit available category choices to those valid for Product
        VALID_CATEGORY_CHOICES = ["WIP", "FINISHED"]
        self.fields["category"].choices = [
            choice
            for choice in models.Material.INVENTORY_CATEGORY_CHOICES
            if choice[0] in VALID_CATEGORY_CHOICES
        ]

        # Initial unit type choice should be 'Each'
        self.fields["unit_type"].initial = "EACH"

    is_available = forms.BooleanField(
        required=False, label="Available to Sales", initial=True
    )

    name_bulk = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "name"}),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean_name_bulk(self):
        """ Name should be unique """
        name_bulk = self.cleaned_data["name_bulk"]
        name_list = name_bulk.split("\r\n")

        for name in name_list:
            objs = models.Product.objects.filter(name=name)
            if self.instance.id:
                objs = objs.exclude(id=self.instance.id)
            if objs.exists():
                raise forms.ValidationError("Product with same name already exists")

        return name_bulk

    class Meta:
        model = models.Product
        fields = (
            "name_bulk",
            "category",
            "production_type",
            "unit_type",
            "is_available",
            "notes",
        )


class ProductCharacteristicsForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCharacteristicsForm, self).__init__(*args, **kwargs)
        # valid_choices = ["WIP", "FINISHED"]
        # self.fields["category"].choices = [
        #     choice
        #     for choice in models.Material.INVENTORY_CATEGORY_CHOICES
        #     if choice[0] in valid_choices
        # ]

    # def clean_name(self):
    #     """ Name should be unique """
    #     valid_choices = ["WIP", "FINISHED"]
    #     objs = models.Item.objects.filter(category__in=valid_choices)
    #     if self.instance.id:
    #         objs = objs.exclude(id=self.instance.id)

    #     name = self.cleaned_data["name"]
    #     if objs.filter(name=name).exists():
    #         raise forms.ValidationError("Product with same name already exists")
    #     return name

    class Meta:
        model = models.ProductCharacteristics
        fields = (
            "description",
            "shelf_life",
            "upc_code",
            "unit_price",
        )


class ResourceForm(BaseModelForm):
    def clean_name(self):
        """ Name should be unique """
        objs = models.Resource.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Resource with same name already exists")
        return name

    class Meta:
        model = models.Resource
        fields = ("name", "capacity", "unit", "resource_type", "stage", "notes")


class ResourceBulkForm(BaseModelForm):

    name_bulk = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "name"}),
    )

    def clean_name_bulk(self):
        """ Name should be unique """
        name_bulk = self.cleaned_data["name_bulk"]
        name_list = name_bulk.split("\r\n")

        for name in name_list:
            objs = models.Resource.objects.filter(name=name)
            if self.instance.id:
                objs = objs.exclude(id=self.instance.id)
            if objs.exists():
                raise forms.ValidationError("Resource with same name already exists")

    class Meta:
        model = models.Resource
        fields = ("name_bulk", "capacity", "unit", "resource_type", "stage", "notes")


class SettingsForm(BaseModelForm):

    default_unit_volume = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="VOLUME"),
        required=False,
        label="Unit (Volume)",
    )

    default_unit_weight = forms.ModelChoiceField(
        queryset=models.UnitMeasurement.objects.filter(unit_type="WEIGHT"),
        required=False,
        label="Unit (Weight)",
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "id": "notes-1"}),
    )

    def clean(self):
        super().clean()
        """ Can only be single instance of settings per app, per tenant """
        if self.instance._state.adding and models.Settings.objects.exists():
            raise forms.ValidationError(
                "There can be only a single Settings instance for each module"
            )

    class Meta:
        model = models.Settings
        fields = (
            "default_unit_weight",
            "default_unit_volume",
            "default_unit_system_weight",
            "default_unit_system_volume",
            "default_target_product_margin",
            "notes",
        )
        widgets = {
            "unit_weight": UnitMeasurementWeightWidget,
            "unit_volume": UnitMeasurementVolumeWidget,
        }


class TeamForm(BaseModelForm):
    def clean_name(self):
        """ Name should be unique """
        objs = models.Team.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Team with same name already exists")
        return name

    class Meta:
        model = models.Team
        fields = ("name", "slug")


class TeamBulkForm(BaseModelForm):

    name_bulk = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "id": "name"}),
    )

    def clean_name_bulk(self):
        """ Name should be unique """
        name_bulk = self.cleaned_data["name_bulk"]
        name_list = name_bulk.split("\r\n")

        for name in name_list:
            objs = models.Team.objects.filter(name=name)
            if self.instance.id:
                objs = objs.exclude(id=self.instance.id)
            if objs.exists():
                raise forms.ValidationError("Team with same name already exists")

    class Meta:
        model = models.Team
        fields = ("name_bulk", "slug")


class UnitMeasurementForm(BaseModelForm):
    """ Name should be unique """

    def clean_name(self):
        objs = models.UnitMeasurement.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        name = self.cleaned_data["name"]
        if objs.filter(name=name).exists():
            raise forms.ValidationError("Unit with same name already exists")
        return name

    def clean_symbol(self):
        """ Symbol should be unique """
        objs = models.UnitMeasurement.objects.all()
        if self.instance.id:
            objs = objs.exclude(id=self.instance.id)

        symbol = self.cleaned_data["symbol"]
        if objs.filter(symbol=symbol).exists():
            raise forms.ValidationError("Unit with same symbol already exists")
        return symbol

    class Meta:
        model = models.UnitMeasurement
        fields = (
            "name",
            "symbol",
            "unit_type",
            "unit_system",
            "display_quantity_smallest",
            "display_quantity_largest",
        )


class UtilityBulkEditExportForm(forms.Form):
    """
    This form and import form (below) will be rendered on same page.
    Select2 only renders one field of given name per page, even if in different forms,
    so format and model fields are prefixed to differentiate
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(UtilityBulkEditExportForm, self).__init__(*args, **kwargs)

    FORMAT_CHOICES = (
        ("XLSX", "Excel (XLSX)"),
        ("CSV", "Comma-Separated (CSV)"),
    )

    MODEL_CHOICES = (
        ("MATERIAL", "Materials"),
        ("MATERIAL_COSTS", "Material Costs"),
        ("PRODUCT", "Products"),
        ("RESOURCES", "Resources"),
    )

    export_format = forms.ChoiceField(
        required=True, choices=FORMAT_CHOICES, label="File Format"
    )

    export_model = forms.ChoiceField(
        required=True, choices=MODEL_CHOICES, label="Model to Export"
    )

    class Meta:
        fields = (
            "export_format",
            "export_model",
        )


class UtilityBulkEditImportForm(forms.Form):
    """
    This form and export form (above) will be rendered on same page.
    Select2 only renders one field of given name per page, even if in different forms,
    so format and model fields are prefixed to differentiate
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(UtilityBulkEditImportForm, self).__init__(*args, **kwargs)

    FORMAT_CHOICES = (
        ("XLSX", "Excel (XLSX)"),
        ("CSV", "Comma-Separated (CSV)"),
    )

    MODEL_CHOICES = (
        ("MATERIAL", "Materials"),
        ("MATERIAL_COSTS", "Material Costs"),
        ("PRODUCT", "Products"),
        ("RESOURCES", "Resources"),
    )

    import_file = forms.FileField(label="Edited File to Upload")

    import_format = forms.ChoiceField(
        required=True, choices=FORMAT_CHOICES, label="File Format"
    )

    import_model = forms.ChoiceField(
        required=True, choices=MODEL_CHOICES, label="Model"
    )

    class Meta:
        fields = (
            "import_file",
            "import_format",
            "import_model",
        )


class UtilityBulkEditConfirmChangesForm(forms.Form):

    confirm = forms.BooleanField(label="Confirm Changes")

    class Meta:
        fields = ("confirm",)


class UtilityBulkUpdateCharacteristicsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(UtilityBulkUpdateCharacteristicsForm, self).__init__(*args, **kwargs)

    contains_crustacea = forms.BooleanField(required=False)
    contains_dairy = forms.BooleanField(required=False)
    contains_egg = forms.BooleanField(required=False)
    contains_fish = forms.BooleanField(required=False)
    contains_peanut = forms.BooleanField(required=False)
    contains_sesame = forms.BooleanField(required=False)
    contains_soy = forms.BooleanField(required=False)
    contains_treenut = forms.BooleanField(required=False)
    contains_wheat = forms.BooleanField(required=False)
    contains_alcohol = forms.BooleanField(required=False)
    contains_gelatin = forms.BooleanField(required=False)
    contains_honey = forms.BooleanField(required=False)
    contains_meat = forms.BooleanField(required=False)

    class Meta:
        fields = [
            "contains_crustacea",
            "contains_dairy",
            "contains_egg",
            "contains_fish",
            "contains_peanut",
            "contains_sesame",
            "contains_soy",
            "contains_treenut",
            "contains_wheat",
            "contains_alcohol",
            "contains_gelatin",
            "contains_honey",
            "contains_meat",
        ]


class UtilityBulkUpdateCharacteristicsConfirmChangesForm(forms.Form):

    confirm = forms.BooleanField(label="Confirm Changes")

    class Meta:
        fields = ("confirm",)

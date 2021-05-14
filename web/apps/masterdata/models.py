# ––– DJANGO IMPORTS
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.db.models.enums import Choices
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal
from django.urls import reverse, reverse_lazy


# ––– PYTHON UTILITY IMPORTS
from decimal import Decimal as D


# –––THIRD-PARTY IMPORTS
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django_pandas.managers import DataFrameManager
from treebeard.mp_tree import MP_Node  # as MaterializedPathNode


# ––– PROJECT IMPORTS
from apps.common import models as common_models
from apps.users import models as users_models


# ––– PARAMETERS


# ––– MODELS

"""
Item
Material
Product
Resource
Team
Settings
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def generate_characteristics():
    return [{}]


# incremented_bill_of_material_version = Signal()


class BillOfMaterials(common_models.HistoryMixin, common_models.AbstractBaseModel):

    version = models.PositiveSmallIntegerField(default=1)
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="bill_of_materials",
    )
    team = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="bills_of_materials"
    )

    # frames = DataFrameManager()
    objects = models.Manager()

    def __str__(self):
        if self.product and self.version:
            return f"{self.product}, v.{self.version}"
        else:
            return f"v. {self.version}"

    def get_absolute_url(self):
        return reverse("masterdata:billofmaterials_detail", kwargs={"pk": self.id})

    def get_procedure_english(self):
        return self.procedures.get(language="eng")

    def get_procedure_espagnol(self):
        return self.procedures.get(language="esp")

    def get_procedure_francais(self):
        return self.procedures.get(language="fra")

    def has_yields(self):
        if hasattr(self, "yields") and any(
            [
                (self.yields.quantity_weight and self.yields.unit_weight),
                (self.yields.quantity_volume and self.yields.unit_volume),
                (
                    self.yields.quantity_each
                    and self.yields.unit_each
                    and self.yields.note_each
                ),
            ]
        ):
            return True
        else:
            return False

    class Meta:
        get_latest_by = ("version",)
        ordering = [
            "-version",
        ]
        verbose_name_plural = "Bills of materials"  # (BoM)"


class BillOfMaterialsCharacteristics(
    common_models.HistoryMixin, common_models.AbstractBaseModel
):
    TEMPERATURE_CHOICES = (
        ("HOT", "Hot"),
        ("AMBIENT", "Ambient"),
        ("COLD", "Cold"),
    )

    version = models.PositiveSmallIntegerField(default=1)

    leadtime = models.PositiveSmallIntegerField(
        default=0, help_text="Lead time, in days"
    )
    temperature_preparation = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    temperature_storage = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    temperature_service = models.CharField(
        max_length=8, choices=TEMPERATURE_CHOICES, null=True, blank=True
    )
    note_production = models.TextField(
        "Production Notes",
        null=True,
        blank=True,
    )

    total_active_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    total_inactive_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    staff_count = models.PositiveSmallIntegerField(default=0)
    note_labor = models.TextField(
        "Labor Notes",
        null=True,
        blank=True,
    )

    bill_of_materials = models.OneToOneField(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="characteristics",
    )

    def __str__(self):
        return f"{self.bill_of_materials.product} | characteristics"

    def get_absolute_url(self):
        """ Only viewable within detail page of parent BOM """
        return reverse(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.bill_of_materials.id},
        )

    class Meta:
        ordering = ["bill_of_materials__product"]
        verbose_name_plural = "BoM characteristics"


class BillOfMaterialsLine(common_models.HistoryMixin, common_models.AbstractBaseModel):
    sequence = models.PositiveSmallIntegerField(null=False, default=1)
    quantity = models.DecimalField(max_digits=8, decimal_places=3, null=False)
    quantity_standard = models.DecimalField(max_digits=8, decimal_places=3, null=False)
    note = models.CharField(max_length=32, null=True, blank=True)
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="lines"
    )
    item = models.ForeignKey("Item", on_delete=models.CASCADE, related_name="lines")

    unit = models.ForeignKey(
        "UnitMeasurement", on_delete=models.CASCADE, related_name="+"
    )
    unit_standard = models.ForeignKey(
        "UnitMeasurement", on_delete=models.CASCADE, related_name="+"
    )

    # frames = DataFrameManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.item.name}"

    def get_item_name(self):
        items = self.bill_of_materials.lines.filter(item__name=self.item.name).order_by(
            "sequence"
        )
        if items.count() > 1:
            return f"{self.item.name} ({self.sequence})"
        return f"{self.item.name}"

    class Meta:
        ordering = ["sequence", "item__name"]
        verbose_name_plural = "BoM lines"


class BillOfMaterialsNote(common_models.HistoryMixin, common_models.AbstractBaseModel):
    note = models.TextField()
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.OneToOneField(
        BillOfMaterials, on_delete=models.CASCADE, related_name="note"
    )

    def __str__(self):
        return f"{self.bill_of_materials.product} | note"

    def get_absolute_url(self):
        """ Only viewable within detail page of parent BOM """
        return reverse(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.bill_of_materials.id},
        )

    class Meta:
        ordering = ["bill_of_materials__product"]
        verbose_name_plural = "BoM notes"


class BillOfMaterialsProcedure(
    common_models.HistoryMixin, common_models.AbstractBaseModel
):
    LANGUAGE_CHOICES = (
        ("eng", "English"),
        ("esp", "Español"),
        ("fra", "Français"),
    )

    procedure = models.TextField()

    language = models.CharField(
        "Language",
        max_length=3,
        choices=LANGUAGE_CHOICES,
        default="eng",
    )
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="procedures",
    )

    def __str__(self):
        return f"{self.bill_of_materials.product} | {self.get_language_display()}"

    def get_absolute_url(self):
        """ Only viewable within detail page of parent BOM """
        return reverse(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.bill_of_materials.id},
        )

    class Meta:
        ordering = ["bill_of_materials", "language"]
        unique_together = [
            "bill_of_materials",
            "language",
        ]
        verbose_name_plural = "BoM procedures"


class BillOfMaterialsResource(
    common_models.HistoryMixin, common_models.AbstractBaseModel
):
    sequence = models.PositiveSmallIntegerField(null=False, default=1)
    capacity_required = models.DecimalField(
        max_digits=8, decimal_places=3, null=False, blank=False
    )
    changeover_required = models.DecimalField(
        max_digits=8, decimal_places=3, null=False, blank=True, default=0
    )
    note = models.CharField(max_length=32, null=True, blank=True)
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="resource_requirements"
    )
    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, related_name="used_in"
    )

    # frames = DataFrameManager()
    objects = models.Manager()

    def __str__(self):
        return f"{self.bill_of_materials} | {self.resource} "

    def get_total_capacity_required(self):
        return capacity_required + changeover_required

    class Meta:
        ordering = ["sequence", "resource"]
        verbose_name_plural = "BoM resources"


class BillOfMaterialsYield(common_models.HistoryMixin, common_models.AbstractBaseModel):
    # each BOM batch can specify a WEIGHT yield, a VOLUME yield and an EACH yield

    yield_noun = models.CharField(
        max_length=24,
        null=True,
        blank=True,
        help_text="Optional descriptor for bulk yields (weight/volume), ie dough, batter, soup",
    )

    quantity_weight = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_weight = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    quantity_weight_standard = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_weight_standard = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    quantity_volume = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_volume = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    quantity_volume_standard = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    unit_volume_standard = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    quantity_each = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    """ note_each field details what, precisely, the "each" unit is
    ie, 36 ea 3" cookies, 72 ea 4" flan tart shells, etc """
    note_each = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Indicate what each unit represents: a 3-inch muffin, a half-size hotel pan, full-size sheet pan, etc",
    )
    unit_each = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    scale_multiple_smallest = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default=D(0.25),
        blank=True,
        help_text="""Smallest practical batch scale possible (possibly limited by discrete ingredient or equipment). If scale smaller than this is requested, the scaled BOM will reflect this scale instead""",
    )
    scale_multiple_largest = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=D(500),
        blank=True,
        help_text="""Largest practical batch scale possible (possibly limited by equipment size,
        like mixer or oven). If scale larger than this is requested, will divide scaled BOM into multiple batches""",
    )
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.OneToOneField(
        BillOfMaterials, on_delete=models.CASCADE, related_name="yields"
    )

    def __str__(self):
        return f"{self.bill_of_materials} | yields"

    def get_absolute_url(self):
        """ Only viewable within detail page of parent BOM """
        return reverse(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.bill_of_materials.id},
        )

    class Meta:
        ordering = ["bill_of_materials__product"]
        verbose_name_plural = "BoM yields"


class BillOfMaterialsTree(MP_Node):
    """Each finished product can only be the root/top-level node of a single tree
    Each WIP product can be a node within multiple trees"""

    name = models.CharField(max_length=96)

    leadtime = models.PositiveSmallIntegerField(
        default=0,
        help_text="Leadtime between when product is made and when it can be used, exclusive of leadtime of any included products",
    )
    quantity_standard = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    scaling_factor = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )

    bill_of_materials = models.OneToOneField(
        BillOfMaterials,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tree",
    )  # if this the root BOM/node (top-level)
    node_bom = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="trees_within"
    )  # this is the node BOM
    unit_standard = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"BOM: {self.name}"

    def return_offset_leadtime(self):
        offset_leadtime = self.leadtime
        for node in self.get_ancestors():
            offset_leadtime += node.leadtime
        return offset_leadtime

    def get_production_offsets(self):
        return {
            "product": self.node_bom.product,
            "bill_of_materials": self.node_bom,
            "parent": self.get_parent(),
            "offset": self.return_offset_leadtime(),
            "scaling_factor": self.scaling_factor,
            "quantity": self.quantity_standard,
            "unit": self.unit_standard,
        }

    class Meta:
        verbose_name_plural = "BoM trees"


def default_cost_table():
    return [{}]


class BillOfMaterialsCost(common_models.ImmutableBaseModel):

    cost_table = models.JSONField(default=default_cost_table)
    input_cost_oldest = models.DateField()
    input_cost_latest = models.DateField()
    total_cost = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        default=D(0),
        null=False,
        blank=False,
    )
    version = models.PositiveSmallIntegerField(default=1)

    bill_of_materials = models.ForeignKey(
        BillOfMaterials, on_delete=models.CASCADE, related_name="costs"
    )

    def __str__(self):
        return f"{self.bill_of_materials} | cost {self.total_cost} | date {self.created_at}"

    class Meta:
        get_latest_by = [
            "-created_at",
        ]
        ordering = ["bill_of_materials", "-created_at"]
        verbose_name_plural = "BoM costs"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ITEM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

""" 
Items are base model of Materials and Products
"""

MATERIAL_VALID_CATEGORIES = [
    "RAW",
    "PREPARED",
    "MRO",
    "OTHER",
    "PACKAGING",
    "SERVICE",
]

PRODUCT_VALID_CATEGORIES = ["WIP", "FINISHED"]


class Item(common_models.HistoryMixin, common_models.AbstractBaseModel):

    INVENTORY_CATEGORY_CHOICES = (
        ("RAW", "Raw Food Ingredient"),
        ("PREPARED", "Prepared Food Ingredient"),
        ("WIP", "Work-in-Progress"),
        ("FINISHED", "Finished Product"),
        ("SERVICE", "Service"),
        ("MRO", "Maintenance/Operating Supplies"),
        ("PACKAGING", "Packaging/Disposable"),
        ("OTHER", "Other/Misc"),
    )

    PRODUCTION_TYPE_CHOICES = (
        ("ORDER", "Make-to-Order"),
        ("STOCK", "Make-to-Stock"),
    )

    UNIT_TYPE_CHOICES = (
        ("WEIGHT", "Weight"),
        ("VOLUME", "Volume"),
        ("EACH", "Each"),
    )

    name = models.CharField("Name", max_length=96, null=False)
    category = models.CharField(
        "Category",
        max_length=32,
        choices=INVENTORY_CATEGORY_CHOICES,
        null=False,
        default="RAW",
    )
    production_type = models.CharField(
        "Production Type",
        max_length=5,
        choices=PRODUCTION_TYPE_CHOICES,
        null=False,
        default="ORDER",
    )
    notes = models.TextField("Notes", null=True, blank=True)
    is_available = models.BooleanField(
        "Available to Sales",
        default=True,
        help_text="Products are available for sale once Approved and if set as Available",
    )
    unit_type = models.CharField(
        "Unit Type",
        max_length=32,
        choices=UNIT_TYPE_CHOICES,
        null=False,
        default="WEIGHT",
    )
    preserve = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    version = models.PositiveSmallIntegerField(default=1)
    version_key = models.CharField(
        max_length=26,
        null=True,
        blank=True,
        editable=False,
    )

    def __str__(self):
        return f"{self.name}"

    def get_assigned_cost(self):
        if self.costs.exists():
            if self.unit_type == "WEIGHT":
                unit_cost = f"{self.costs.latest().unit_cost_weight}"
                unit = Settings.objects.get().default_unit_weight
                unit_str = f"per {unit.symbol}"
            elif self.unit_type == "VOLUME":
                unit_cost = f"{self.costs.latest().unit_cost_volume}"
                unit = Settings.objects.get().default_unit_weight
                unit_str = f"per {unit.symbol}"
            elif self.unit_type == "EACH":
                unit_cost = f"{self.costs.latest().unit_cost_each}"
                unit_str = "per each"
            else:
                unit_cost = f"{D(0.00)}"
                unit_str = None
            return f"$ {unit_cost} {unit_str}"
        else:
            return "No costs entered yet"

    def get_bill_of_materials(self):
        return self.bills_of_materials.filter(state="APPROVED").latest()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self._state.adding:
            created = True
            self.version_key = self.id
        else:
            created = False
        super().save(*args, **kwargs)
        if created:
            ItemCharacteristics.objects.create(item=self)
            ItemCost.objects.create(item=self)
        if created and self.category in PRODUCT_VALID_CATEGORIES:
            ProductStatus.objects.create(product=self)

    class Meta:
        ordering = [
            "name",
            "version",
        ]
        get_latest_by = ["version"]


def check_if_all_bool(*, elements: list) -> bool:
    """ Check if all elements in list are either True or False """
    result = True
    for element in elements:
        if not isinstance(element, bool):
            return False
    return result


def check_if_all_none(*, elements: list) -> bool:
    """ Check if all elements in list are None """
    result = True
    for element in elements:
        if element is not None:
            return False
    return result


def check_if_mixed_bool_and_none(*, elements: list) -> bool:
    """ Check if elements in list are mix of boolean values (True/False) and None (neither all one or the other) """
    found_bool = False
    found_none = False
    for element in elements:
        if isinstance(element, bool):
            found_bool = True
        if element is None:
            found_none = True
    if all([found_bool, found_none]):
        return True
    else:
        return False


class ItemCharacteristics(common_models.HistoryMixin, common_models.AbstractBaseModel):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    EVALUATION_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("NAN", "No Evaluation Necessary"),
    )

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approved Necessary"),
    )

    # Allergen & Ingredient Attributes

    contains_alcohol = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain alcohol?",
    )
    contains_crustacea = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?",
    )
    contains_dairy = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain dairy?",
    )
    contains_egg = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain egg?",
    )
    contains_fish = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain fish?",
    )
    contains_gelatin = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain gelatin?",
    )
    contains_honey = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain honey?",
    )
    contains_meat = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain meat/meat products?",
    )
    contains_peanut = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain peanuts?",
    )
    contains_sesame = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain sesame?",
    )
    contains_soy = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain soy?",
    )
    contains_treenut = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain treenuts (not peanuts)?",
    )
    contains_wheat = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="Does this material or product contain wheat?",
    )
    ingredients = models.TextField(null=True, blank=True)
    allergens_evaluated = models.CharField(
        max_length=12, choices=EVALUATION_CHOICES, default="PENDING", blank=True
    )

    # Sales & Marketing Attributes

    description = models.TextField(
        "Description for menus, sales & marketing",
        default="",
        blank=True,
    )
    shelf_life = models.PositiveIntegerField("Shelf Life (days)", default=0)
    unit_price = models.DecimalField(
        "List price per unit of product",
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        default=0.00,
    )
    upc_code = models.CharField(
        "UPC Code", max_length=12, null=True, blank=True
    )  # GTIN-12/UPC-A
    version = models.PositiveSmallIntegerField(default=1)
    state = FSMField(
        default="PENDING",
        verbose_name="Status",
        choices=STATE_CHOICES,
    )

    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name="characteristics"
    )

    def __str__(self):
        return f"{self.item.name}"

    def save(self, *args, **kwargs):
        allergen_fields = [
            self.contains_crustacea,
            self.contains_dairy,
            self.contains_egg,
            self.contains_fish,
            self.contains_gelatin,
            self.contains_honey,
            self.contains_meat,
            self.contains_peanut,
            self.contains_sesame,
            self.contains_soy,
            self.contains_treenut,
            self.contains_wheat,
            self.contains_alcohol,
        ]

        if check_if_all_none(elements=allergen_fields):
            self.allergens_evaluated = "PENDING"
        if check_if_mixed_bool_and_none(elements=allergen_fields):
            self.allergens_evaluated = "IN_PROGRESS"
        if check_if_all_bool(elements=allergen_fields):
            if self.item.category == "RAW":
                self.allergens_evaluated = "COMPLETED"

        self.full_clean()
        return super().save(*args, **kwargs)

    # States:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # PENDING (Default) - item has not been evaluated for allergens
    # APPROVED - item has allergen matrix completed and, if not base item, has ingredient statement entered
    # DISQUALIFIED - item violates one or more constraints for production (allergen, preference, religious restrictions)
    # NO APPROVAL NEEDED - item is category MRO/PACKAGING/SERVICE or otherwise does not need evaluation for allergens
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Items PENDING or DISQUALIFIED cannot be added to recipe/BOM
    # Items transitioning to PENDING or DISQUALIFIED will trigger blocks on recipes/BOMs containing them

    @transition(field=state, source="*", target="APPROVED")
    def approved(self):
        return

    @transition(field=state, source="*", target="DISQUALIFIED")
    def disqualify(self):
        return

    @transition(field=state, source="*", target="NAN")
    def no_approval_needed(self):
        return

    @transition(field=state, source="*", target="PENDING")
    def set_pending(self):
        return

    class Meta:
        get_latest_by = ["version"]
        verbose_name_plural = "Item characteristics"


class ItemCost(common_models.ImmutableBaseModel):

    BASIS_CHOICES = [
        ("DIRECT", "Directly Assigned"),
        ("CALCULATED", "Calculated"),
        ("NAIVE", "Naïve"),
        ("CUMULATIVE", "Cumulative"),
        ("MA3", "Moving Average (3)"),
        ("MA5", "Moving Average (5)"),
        ("MA7", "Moving Average (5)"),
        ("EXP", "Exponential Smoothing"),
    ]

    unit_cost_weight = models.DecimalField(
        "Cost per unit, weight, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    unit_cost_volume = models.DecimalField(
        "Cost per unit, volume (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    unit_cost_each = models.DecimalField(
        "Cost per each",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    basis = models.CharField(
        "Assignment basis", max_length=24, choices=BASIS_CHOICES, default="DIRECT"
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="costs")

    def __str__(self):
        return f"{self.item.name} | {self.created_at} assigned cost"

    class Meta:
        ordering = ["created_at"]
        get_latest_by = ["created_at"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

"""
Material is a proxy model of Item
Materials are sourceable items that are used in production of Products
Materials have category of RAW, MRO, OTHER, PACKAGING or SERVICE
"""


class MaterialManager(models.Manager):
    def get_queryset(self):
        return (
            super(MaterialManager, self)
            .get_queryset()
            .filter(category__in=MATERIAL_VALID_CATEGORIES)
        )


class MaterialRelatedManager(models.Manager):
    def get_queryset(self):
        return (
            super(MaterialRelatedManager, self)
            .get_queryset()
            .filter(item__category__in=MATERIAL_VALID_CATEGORIES)
        )


class Material(Item):
    objects = MaterialManager()

    def get_absolute_url(self):
        return reverse("masterdata:material_detail", kwargs={"pk": self.id})

    class Meta:
        proxy = True
        permissions = [
            (
                "change_material_deletion_protection",
                "Can change deletion protection of material",
            ),
            (
                "schedule_permanent_material_deletion",
                "Can permanently delete material information",
            ),
        ]


class MaterialCharacteristics(ItemCharacteristics):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)
    objects = MaterialRelatedManager()

    class Meta:
        proxy = True
        verbose_name_plural = "Material characteristics"


class MaterialCost(ItemCost):
    objects = MaterialRelatedManager()

    class Meta:
        proxy = True


# ––––––––––––––-––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

"""
Product is a proxy model of Item
Products are manufactured items that use/consume Materials and Products as specified in a Bill of Materials
Products have category of WIP or FINISHED
"""


class ProductManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductManager, self)
            .get_queryset()
            .filter(category__in=PRODUCT_VALID_CATEGORIES)
        )


class ProductRelatedManager(models.Manager):
    def get_queryset(self):
        return (
            super(ProductRelatedManager, self)
            .get_queryset()
            .filter(item__category__in=PRODUCT_VALID_CATEGORIES)
        )


class Product(Item):
    objects = ProductManager()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("masterdata:product_detail", kwargs={"pk": self.id})


class ProductCharacteristics(ItemCharacteristics):
    """ if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate) """

    objects = ProductRelatedManager()

    class Meta:
        proxy = True
        verbose_name_plural = "Product characteristics"


class ProductCost(ItemCost):
    objects = ProductRelatedManager()

    class Meta:
        proxy = True


class ProductStatus(common_models.AbstractBaseModel):

    STATE_CHOICES = [
        ("DRAFT", "Draft"),
        ("AWAITING", "Awaiting Approval"),
        ("RETURNED", "Returned for Revisions"),
        ("APPROVED", "Approved"),
        ("SUPERSEDED", "Superseded"),
    ]

    version = models.PositiveSmallIntegerField(default=1)
    state = FSMField(
        default="DRAFT",
        verbose_name="State",
        choices=STATE_CHOICES,
    )

    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="status",
    )

    def __str__(self):
        return f"{self.product}, v.{self.product.version}"

    # Status:
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # DRAFT (Default) - BOM is in development and is not available for sale or production
    # AWAITING APPROVAL - BOM has been submitted for approval and is not available for sale or production
    # RETURNED FOR REVISION - BOM has been returned for further development, is not available for sale or production
    # APPROVED - BOM is approved and may be ordered for sale and produced
    # SUPERSEDED - BOM has been superseded by later version, which may or may not be currently active
    # INACTIVE - previously-approved BOM is currently inactive and is not available for sale or production

    @fsm_log_by
    @transition(
        field=state, source="*", target="DRAFT", permission="app.change_product_status"
    )
    def set_draft(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source=["DRAFT", "RETURNED"],
        target="AWAITING",
        permission=["app.change_product_status", "app.submit_product_for_approval"],
    )
    def submit_for_approval(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="*",
        target="RETURNED",
        permission="app.change_product_status",
    )
    def return_for_revision(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="AWAITING",
        target="APPROVED",
        permission="app.change_product_status",
    )
    def approve(self, by=None):
        return

    @fsm_log_by
    @transition(
        field=state,
        source="APPROVED",
        target="SUPERSEDED",
        permission="app.change_product_status",
    )
    def supersede(self, by=None):
        return

    class Meta:
        get_latest_by = ("version",)
        ordering = [
            "-version",
            "state",
        ]
        permissions = [
            ("change_product_status", "Can change status of Product"),
            ("submit_product_for_approval", "Can submit Product for approval"),
        ]
        verbose_name_plural = "Product statuses"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# RESOURCE
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Resource(common_models.HistoryMixin, common_models.AbstractBaseModel):

    RESOURCE_TYPE_CHOICES = (
        ("TIME", "Time-Dependent"),
        ("SPACE", "Space-Dependent"),
    )

    STAGE_CHOICES = (
        ("WORKING", "Working"),
        ("STORAGE", "Storage"),
    )

    capacity = models.PositiveBigIntegerField(
        "Capacity",
        null=False,
        blank=False,
        default=0,
        help_text="""
        If the resource is <strong>time-dependent</strong>, the <strong>capacity</strong> represents
        how many units are available <strong>per hour</strong><br/>
        If the resource is <strong>space-dependent</strong>, the <strong>capacity</strong> represents
        how many units are available <strong>in the working facility</strong><br/>
        """,
    )
    name = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        help_text="""
    The name of the <strong>resource</strong> (example: oven, freezer, mixer),<br/>
    not the name of the <strong>unit</strong> (example: oven rack-minutes, speed rack-shelves, mixer bowl-minutes)
    """,
    )
    notes = models.TextField(null=True, blank=True)
    resource_type = models.CharField(
        max_length=8, choices=RESOURCE_TYPE_CHOICES, default="TIME"
    )
    stage = models.CharField(
        max_length=8,
        choices=STAGE_CHOICES,
        default="WORKING",
        help_text="""
        At the <strong>working</strong> stage, resources are used for a known, bounded amount of time (like a mixer or an oven)<br/>
        At the <strong>storage</strong> stage, resources are used for a indeterminate amount of time (like a freezer)
        """,
    )
    unit = models.CharField(
        max_length=32,
        null=True,
        help_text="""
        Describe units of utilization (ie, oven rack-minutes) that production consumes<br/>
        If the resource is <strong>time-dependent</strong>, the <strong>unit</strong> should be expressed in terms of <strong>minutes</strong><br/>
        If the resource is <strong>space-dependent</strong>, the <strong>unit</strong> should be expressed in terms of <strong>area</strong><br/>
        """,
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("masterdata:resource_detail", kwargs={"pk": self.id})

    class Meta:
        ordering = ["name"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Team(common_models.HistoryMixin, common_models.AbstractBaseModel):
    name = models.CharField("Team name", max_length=32, null=True)
    slug = models.SlugField(max_length=32, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("masterdata:team_detail", kwargs={"pk": self.id})

    class Meta:
        ordering = ["name"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# UNIT OF MEASUREMENT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UnitMeasurement(common_models.HistoryMixin, common_models.AbstractBaseModel):
    UNIT_TYPE_CHOICES = (
        ("WEIGHT", "Weight"),
        ("VOLUME", "Volume"),
        ("EACH", "Each"),
        ("MISC", "Miscellaneous"),
        ("INVENTORY", "Inventory"),
    )

    UNIT_SYSTEM_CHOICES = (
        ("METRIC", "Metric"),
        ("US", "US Customary"),
        ("NA", "Does not apply"),
    )

    name = models.CharField("Name", max_length=32, null=False, unique=True)
    symbol = models.CharField("Symbol", max_length=9, null=False)
    unit_system = models.CharField(
        "System", max_length=6, choices=UNIT_SYSTEM_CHOICES, default="NA"
    )
    unit_type = models.CharField(
        "Type", max_length=12, choices=UNIT_TYPE_CHOICES, default="WEIGHT"
    )
    display_quantity_smallest = models.DecimalField(
        "Smallest quantity to display (if possible)",
        max_digits=4,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.125,
    )
    display_quantity_largest = models.DecimalField(
        "Largest quantity to display (if possible)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=1000,
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("masterdata:unitmeasurement_detail", kwargs={"pk": self.id})

    class Meta:
        ordering = [
            "unit_type",
            "name",
        ]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(common_models.HistoryMixin, common_models.AbstractBaseModel):
    """ MasterData settings """

    default_unit_weight = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    default_unit_volume = models.ForeignKey(
        "UnitMeasurement",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    default_unit_system_weight = models.CharField(
        max_length=12, choices=UnitMeasurement.UNIT_SYSTEM_CHOICES, default="US"
    )
    default_unit_system_volume = models.CharField(
        max_length=12, choices=UnitMeasurement.UNIT_SYSTEM_CHOICES, default="US"
    )

    default_target_product_margin = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Enter default suggested margin as a proportion of material cost",
    )

    def __str__(self):
        return f"Settings for MasterData app"

    def clean(self):
        if self.default_unit_weight:
            if self.default_unit_weight.unit_system != self.default_unit_system_weight:
                raise ValidationError("Defaults for unit and unit system must match")

        if self.default_unit_volume:
            if self.default_unit_volume.unit_system != self.default_unit_system_volume:
                raise ValidationError("Defaults for unit and unit system must match")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        permissions = [
            (
                "change_masterdata_settings",
                "Can change MasterData settings",
            ),
        ]
        verbose_name_plural = "Settings"
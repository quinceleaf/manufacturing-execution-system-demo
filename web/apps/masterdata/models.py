# ––– DJANGO IMPORTS
from django.core.exceptions import ValidationError
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
# ITEM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

""" 
Items are base model of Materials and Products
"""


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

    STATE_CHOICES = (
        ("AVAIL", "Available"),
        ("UNAVAIL", "Unavailable"),
    )

    UNIT_TYPE_CHOICES = (
        ("WEIGHT", "Weight"),
        ("VOLUME", "Volume"),
        ("EACH", "Each"),
        ("MISC", "Miscellaneous"),
        ("INVENTORY", "Inventory"),
    )

    name = models.CharField("Name", max_length=96, null=False)
    category = models.CharField(
        "Category",
        max_length=32,
        choices=INVENTORY_CATEGORY_CHOICES,
        null=False,
        default="RAW",
    )

    notes = models.TextField("Notes", null=True, blank=True)
    state = models.CharField(
        "Status",
        max_length=10,
        choices=STATE_CHOICES,
        null=False,
        default="AVAIL",
    )
    unit_type = models.CharField(
        "Unit Type",
        max_length=32,
        choices=UNIT_TYPE_CHOICES,
        null=False,
        default="WEIGHT",
    )
    preserve = models.BooleanField(default=False)
    version = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

    def get_assigned_cost(self):
        if self.costs.exists():
            if self.unit_type == "WEIGHT":
                return f"{self.costs.latest().unit_cost_weight}"
            elif self.unit_type == "VOLUME":
                return f"{self.costs.latest().unit_cost_volume}"
            elif self.unit_type == "EACH":
                return f"{self.costs.latest().unit_cost_each}"
            else:
                return f"{D(0.00)}"
        else:
            return "No costs entered yet"

    def get_bill_of_materials(self):
        return self.bills_of_materials.filter(state="APPROVED").latest()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self._state.adding:
            created = True
        else:
            created = False
        super().save(*args, **kwargs)
        if created:
            ItemCharacteristics.objects.create(item=self)
            ItemConversion.objects.create(item=self)
            ItemCost.objects.create(item=self)

    class Meta:
        ordering = ["name"]
        get_latest_by = ["version"]


class ItemCharacteristics(common_models.HistoryMixin, common_models.AbstractBaseModel):
    # if category RAW/WIP/FINISHED must have allergen matrix (and ingredient statement, if appropriate)

    ALLERGEN_CHOICES = (
        ("UNEVAL", "Pending"),
        ("PRESENT", "Pending"),
        ("ABSENT", "Pending"),
    )

    STATE_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("DISQUALIFIED", "Disqualifed"),
        ("NAN", "No Approved Necessary"),
    )

    contains_alcohol = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain alcohol?",
    )
    contains_crustacea = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?",
    )
    contains_dairy = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain dairy?",
    )
    contains_egg = models.BooleanField(
        null=True, default=None, help_text="Does this material or product contain egg?"
    )
    contains_fish = models.BooleanField(
        null=True, default=None, help_text="Does this material or product contain fish?"
    )
    contains_gelatin = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain gelatin?",
    )
    contains_honey = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain honey?",
    )
    contains_meat = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain meat/meat products?",
    )
    contains_peanut = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain peanuts?",
    )
    contains_sesame = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain sesame?",
    )
    contains_soy = models.BooleanField(
        null=True, default=None, help_text="Does this material or product contain soy?"
    )
    contains_treenut = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain treenuts (not peanuts)?",
    )
    contains_wheat = models.BooleanField(
        null=True,
        default=None,
        help_text="Does this material or product contain wheat?",
    )

    description = models.TextField(
        "Description for menus, sales & marketing",
        default="",
        blank=True,
    )
    ingredients = models.TextField(null=True, blank=True)
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
        # protected=True,
    )

    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name="characteristics"
    )

    def __str__(self):
        return f"{self.item.name} | characteristics"

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


class ItemConversion(common_models.HistoryMixin, common_models.AbstractBaseModel):

    allowed_weight = models.BooleanField(null=True, default=True)
    allowed_volume = models.BooleanField(default=False)
    allowed_each = models.BooleanField(default=False)
    ratio_weight_to_volume = models.DecimalField(
        "Ratio of weight to volume, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    ratio_weight_to_each = models.DecimalField(
        "Ratio of weight to each, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    ratio_volume_to_each = models.DecimalField(
        "Ratio of volume to each, (standardized)",
        max_digits=7,
        decimal_places=3,
        null=False,
        blank=False,
        default=0.000,
    )
    version = models.PositiveSmallIntegerField(default=1)

    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name="conversion"
    )

    def __str__(self):
        return f"{self.item.name} | conversion"

    class Meta:
        get_latest_by = ["version"]


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
        valid_categories = [
            "RAW",
            "PREPARED",
            "MRO",
            "OTHER",
            "PACKAGING",
            "SERVICE",
        ]
        return (
            super(MaterialManager, self)
            .get_queryset()
            .filter(category__in=valid_categories)
        )


class MaterialRelatedManager(models.Manager):
    def get_queryset(self):
        valid_categories = [
            "RAW",
            "PREPARED",
            "OTHER",
            "PACKAGING",
            "SERVICE",
        ]
        return (
            super(MaterialRelatedManager, self)
            .get_queryset()
            .filter(item__category__in=valid_categories)
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


class MaterialConversion(ItemConversion):
    objects = MaterialRelatedManager()

    class Meta:
        proxy = True


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
        valid_categories = ["WIP", "FINISHED"]
        return (
            super(ProductManager, self)
            .get_queryset()
            .filter(category__in=valid_categories)
        )


class ProductRelatedManager(models.Manager):
    def get_queryset(self):
        valid_categories = ["WIP", "FINISHED"]
        return (
            super(ProductRelatedManager, self)
            .get_queryset()
            .filter(item__category__in=valid_categories)
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


class ProductConversion(ItemConversion):
    objects = ProductRelatedManager()

    class Meta:
        proxy = True


class ProductCost(ItemCost):
    objects = ProductRelatedManager()

    class Meta:
        proxy = True


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
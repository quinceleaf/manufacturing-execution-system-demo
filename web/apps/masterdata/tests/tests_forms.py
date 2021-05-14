# ––– DJANGO IMPORTS
from django.test import TestCase


# --- PYTHON UTILITY IMPORTS
import random


# –––THIRD-PARTY IMPORTS
from model_bakery import baker


# ––– PROJECT IMPORTS
from apps.masterdata import models, forms


"""
Tests for forms:

BillOfMaterialsCharacteristicsForm
BillOfMaterialsLineChoiceField
BillOfMaterialsLineForm
BillOfMaterialsLineFormSet
BillOfMaterialsNoteForm
BillOfMaterialsProcedureForm
BillOfMaterialsResourceForm
BillOfMaterialsResourceFormSet
BillOfMaterialsScaleForm
BillOfMaterialsYieldForm

MaterialBulkForm -x
MaterialForm -x

ProductBulkForm -x
ProductCharacteristicsForm
ProductForm -x

ResourceBulkForm
ResourceForm

SettingsForm

TeamBulkForm
TeamForm

UnitMeasurementForm

UtilityBulkEditConfirmChangesForm
UtilityBulkEditExportForm
UtilityBulkEditImportForm
UtilityBulkUpdateCharacteristicsConfirmChangesForm
UtilityBulkUpdateCharacteristicsForm

"""


class MaterialFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Material
        cls.form = forms.MaterialForm

        cls.VALID_CATEGORY_CHOICES = (
            ("RAW", "Raw Food Ingredient"),
            ("PREPARED", "Prepared Food Ingredient"),
            ("SERVICE", "Service"),
            ("MRO", "Maintenance/Operating Supplies"),
            ("PACKAGING", "Packaging/Disposable"),
            ("OTHER", "Other/Misc"),
        )

        valid_name = "Default material"
        cls.duplicate_name = "Default material"

        valid_category = "RAW"
        cls.invalid_category = "FINISHED"

        cls.model_instance = baker.make(
            cls.model, name=valid_name, category=valid_category
        )

    def test_category_must_be_valid(cls):
        """ Name submitted for Material must not match any existing Material """

        form = cls.form(
            data={
                "name": "Flour, all-purpose",
                "category": cls.invalid_category,
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["category"][0],
            f"Select a valid choice. {cls.invalid_category} is not one of the available choices.",
        )

    def test_name_must_be_unique(cls):
        form = cls.form(
            data={
                "name": cls.duplicate_name,
                "category": random.choice(cls.VALID_CATEGORY_CHOICES)[0],
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name"][0], "Material with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class MaterialBulkFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Material
        cls.form = forms.MaterialBulkForm

        cls.VALID_CATEGORY_CHOICES = (
            ("RAW", "Raw Food Ingredient"),
            ("PREPARED", "Prepared Food Ingredient"),
            ("SERVICE", "Service"),
            ("MRO", "Maintenance/Operating Supplies"),
            ("PACKAGING", "Packaging/Disposable"),
            ("OTHER", "Other/Misc"),
        )

        valid_name = "Default material"
        cls.valid_name_bulk = "Default material 2\r\nDefault material 3\r\nDefault material 4\r\nDefault material 5\r\n"
        cls.invalid_name_bulk = "Default material 2\r\nDefault material\r\nDefault material 4\r\nDefault material 5\r\n"

        valid_category = "RAW"
        cls.invalid_category = "FINISHED"

        cls.model_instance = baker.make(
            cls.model, name=valid_name, category=valid_category
        )

    def test_category_must_be_valid(cls):
        form = cls.form(
            data={
                "name_bulk": cls.valid_name_bulk,
                "category": cls.invalid_category,
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["category"][0],
            f"Select a valid choice. {cls.invalid_category} is not one of the available choices.",
        )

    def test_name_bulk_must_be_unique(cls):
        """ Each Material name submitted in the list of names during bulk creation must not match any existing Material """
        form = cls.form(
            data={
                "name_bulk": cls.invalid_name_bulk,
                "category": random.choice(cls.VALID_CATEGORY_CHOICES)[0],
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name_bulk"][0], "Material with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class ProductFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Product
        cls.form = forms.ProductForm

        cls.VALID_CATEGORY_CHOICES = (
            ("WIP", "Work-in-Progress"),
            ("FINISHED", "Finished Product"),
        )

        valid_name = "Default product"
        cls.duplicate_name = "Default product"

        valid_category = "FINISHED"
        cls.invalid_category = "PACKAGING"

        cls.model_instance = baker.make(
            cls.model, name=valid_name, category=valid_category
        )

    def test_category_must_be_valid(cls):
        form = cls.form(
            data={
                "name": "Muffin, blueberry",
                "category": cls.invalid_category,
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["category"][0],
            f"Select a valid choice. {cls.invalid_category} is not one of the available choices.",
        )

    def test_name_must_be_unique(cls):
        """ Name submitted for Product must not match any existing Product """
        form = cls.form(
            data={
                "name": cls.duplicate_name,
                "category": random.choice(cls.VALID_CATEGORY_CHOICES)[0],
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(form.errors["name"][0], "Product with same name already exists")

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class ProductBulkFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Product
        cls.form = forms.ProductBulkForm

        cls.VALID_CATEGORY_CHOICES = (
            ("WIP", "Work-in-Progress"),
            ("FINISHED", "Finished Product"),
        )

        valid_name = "Default product"
        cls.valid_name_bulk = "Default product 2\r\nDefault product 3\r\nDefault product 4\r\nDefault product 5\r\n"
        cls.invalid_name_bulk = "Default product 2\r\nDefault product\r\nDefault product 4\r\nDefault product 5\r\n"

        valid_category = "WIP"
        cls.invalid_category = "PACKAGING"

        cls.model_instance = baker.make(
            cls.model, name=valid_name, category=valid_category
        )

    def test_category_must_be_valid(cls):
        form = cls.form(
            data={
                "name_bulk": cls.valid_name_bulk,
                "category": cls.invalid_category,
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["category"][0],
            f"Select a valid choice. {cls.invalid_category} is not one of the available choices.",
        )

    def test_name_bulk_must_be_unique(cls):
        """ Each Product name submitted in the list of names during bulk creation must not match any existing Product """
        form = cls.form(
            data={
                "name_bulk": cls.invalid_name_bulk,
                "category": random.choice(cls.VALID_CATEGORY_CHOICES)[0],
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "state": random.choice(cls.model.STATE_CHOICES)[0],
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name_bulk"][0], "Product with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class ResourceFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Resource
        cls.form = forms.ResourceForm

        valid_name = "Resource 1"
        cls.duplicate_name = "Resource 1"

        cls.model_instance = baker.make(cls.model, name=valid_name)

    def test_name_must_be_unique(cls):
        """ Name submitted for Resource must not match any existing Resource """
        form = cls.form(
            data={
                "name": cls.duplicate_name,
                "unit": "mixer bowl-minutes",
                "stage": random.choice(cls.model.STAGE_CHOICES)[0],
                "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
                "capacity": random.randint(10, 20),
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name"][0], "Resource with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class ResourceBulkFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Resource
        cls.form = forms.ResourceBulkForm

        valid_name = "Resource 1"
        cls.valid_name_bulk = "Resource 2\r\nResource 3\r\nResource 4\r\nResource 5\r\n"
        cls.invalid_name_bulk = (
            "Resource 2\r\nResource 1\r\nResource 4\r\nResource 5\r\n"
        )

        cls.model_instance = baker.make(cls.model, name=valid_name)

    def test_name_bulk_must_be_unique(cls):
        """ Each Resource name submitted in the list of names during bulk creation must not match any existing Resource """
        form = cls.form(
            data={
                "name_bulk": cls.invalid_name_bulk,
                "unit": "mixer bowl-minutes",
                "stage": random.choice(cls.model.STAGE_CHOICES)[0],
                "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
                "capacity": random.randint(10, 20),
                "notes": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name_bulk"][0], "Resource with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class TeamFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Team
        cls.form = forms.TeamForm

        valid_name = "Team 1"
        cls.duplicate_name = "Team 1"

        cls.model_instance = baker.make(cls.model, name=valid_name)

    def test_name_must_be_unique(cls):
        """ Name submitted for Team must not match any existing Team """
        form = cls.form(
            data={
                "name": cls.duplicate_name,
                "slug": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(form.errors["name"][0], "Team with same name already exists")

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class TeamBulkFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.Team
        cls.form = forms.TeamBulkForm

        valid_name = "Team 1"
        cls.valid_name_bulk = "Team 2\r\nTeam 3\r\nTeam 4\r\nTeam 5\r\n"
        cls.invalid_name_bulk = "Team 2\r\nTeam 1\r\nTeam 4\r\nTeam 5\r\n"

        cls.model_instance = baker.make(cls.model, name=valid_name)

    def test_name_bulk_must_be_unique(cls):
        """ Each name submitted in the list of names during bulk creation must not match any existing Team """
        form = cls.form(
            data={
                "name_bulk": cls.invalid_name_bulk,
                "slug": "",
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["name_bulk"][0], "Team with same name already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass


class UnitMeasurementFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.model = models.UnitMeasurement
        cls.form = forms.UnitMeasurementForm

        valid_name = "Unit 1"
        cls.duplicate_name = "Unit 1"

        valid_symbol = "g"
        cls.duplicate_symbol = "g"

        cls.model_instance = baker.make(cls.model, name=valid_name, symbol=valid_symbol)

    def test_name_must_be_unique(cls):
        """ Name submitted for UnitMeasurement must not match any existing UnitMeasurement """

        form = cls.form(
            data={
                "name": cls.duplicate_name,
                "symbol": "kg",
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
                "display_quantity_smallest": 0.125,
                "display_quantity_largest": 1000,
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(form.errors["name"][0], "Unit with same name already exists")

    def test_symbol_must_be_unique(cls):
        """ Symbol submitted for UnitMeasurement must not match any existing UnitMeasurement """

        form = cls.form(
            data={
                "name": "Unit 2",
                "symbol": cls.duplicate_symbol,
                "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
                "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
                "display_quantity_smallest": 0.125,
                "display_quantity_largest": 1000,
            }
        )
        cls.assertFalse(form.is_valid())
        cls.assertEqual(
            form.errors["symbol"][0], "Unit with same symbol already exists"
        )

    @classmethod
    def tearDownClass(cls):
        """ Cleanup tasks """
        pass

# ––– DJANGO IMPORTS
from django.test import TestCase


# –––THIRD-PARTY IMPORTS
from model_bakery import baker


# ––– PROJECT IMPORTS
from apps.masterdata import models


"""
Tests for models:

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

"""

Models:
- test fields
- test relationships
- test methods (if applicable)
- Any associated actions
- Additional model methods
- For models with FSM defined workflows, test flow and side effects (if any)


"""


class TestMaterialModel(TestCase):
    def setUp(self):
        """ initialization """

        self.TEST_NAME = "Blueberries, IQF"

        self.m = baker.make(models.Material, name=self.TEST_NAME)

    def test_create_material(self):
        self.assertIsInstance(self.m, models.Material)

    def test_update_material(self):
        self.assertIsInstance(self.m, models.Material)

    def test_delete_material(self):
        self.assertIsInstance(self.m, models.Material)

    def test_str_representation(self):
        name = f"{self.m.name}"
        self.assertEquals(str(self.m), name)

    def tearDown(self):
        """ cleanup tasks """
        pass


class TestTeamModel(TestCase):
    def setUp(self):
        """ initialization """

        self.TEST_NAME = "Packaging Team"

        self.m = baker.make(models.Team, name=self.TEST_NAME)

    def test_create_team(self):
        self.assertIsInstance(self.m, models.Team)

    def test_update_team(self):
        self.assertIsInstance(self.m, models.Team)

    def test_delete_team(self):
        self.assertIsInstance(self.m, models.Team)

    def test_str_representation(self):
        name = f"{self.m.name}"
        self.assertEquals(str(self.m), name)

    def tearDown(self):
        """ cleanup tasks """
        pass
# ––– DJANGO IMPORTS
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse


# ––– PYTHON UTILITY IMPORTS
import random


# ––– THIRD-PARTY IMPORTS
from faker import Faker
from model_bakery import baker


# ––– PROJECT IMPORTS
from apps.masterdata import models, views
from apps.users import models as users_models

faker = Faker()

"""
Tests for views:

BillOfMaterials
BillOfMaterialsCharacteristics
BillOfMaterialsLine
BillOfMaterialsNote
BillOfMaterialsProcedure
BillOfMaterialsTree
BillOfMaterialsYields

Material (PROXY of Item)
MaterialCharacteristics (PROXY of ItemCharacteristics)
MaterialCost (PROXY of ItemCost)
MaterialConversion (PROXY of ItemConversion)

Product (PROXY of Item)
ProductCharacteristics (PROXY of ItemCharacteristics)
ProductCost (PROXY of ItemCost)
ProductConversion (PROXY of ItemConversion)

Resource
Team
Settings

"""

"""

CRUD - List view, auth'ed w/o permissions vs auth'ed w/permissions vs anonymous
CRUD - Detail view, auth'ed w/o permissions vs auth'ed w/permissions vs anonymous
CRUD - Create view, auth'ed w/o permissions vs auth'ed w/permissions vs anonymous
CRUD - Update view, auth'ed w/o permissions vs auth'ed w/permissions vs anonymous
CRUD - Delete view (if appropriate), auth'ed w/o permissions vs auth'ed w/permissions vs anonymous

"""


class TestMaterialViews(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initialize this TestCase """

        super().setUpClass()

        # Create client for handling requests
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        """ Set up data for all tests within this TestCase """

        # Create a user instance for authenticated views
        cls.user = users_models.User.objects.create(
            username=faker.user_name(),
            email=faker.email(),
        )
        cls.user.set_password(faker.password(length=random.randint(12, 24)))
        cls.user.save()

        cls.model = models.Material

        # Material is a proxy model of Item, differentiated on the basis of categories
        # So for the test model instance generation and mutation must constrain the choices
        cls.VALID_CATEGORY_CHOICES = (
            ("RAW", "Raw Food Ingredient"),
            ("PREPARED", "Prepared Food Ingredient"),
            ("SERVICE", "Service"),
            ("MRO", "Maintenance/Operating Supplies"),
            ("PACKAGING", "Packaging/Disposable"),
            ("OTHER", "Other/Misc"),
        )

        # Create model instance
        name = "Chocolate, bittersweet"
        category = "PREPARED"
        cls.model_instance = baker.make(models.Material, name=name, category=category)

        cls.expected_listview_title = "<title>Materials</title>"
        cls.expected_detailview_title = f"<title>{cls.model_instance.name}</title>"

        cls.valid_form = {
            "name": "Chocolate, white",
            "category": "PREPARED",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_form = {
            "name": "",
            "category": "MRO",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        cls.valid_update_form = {
            "name": "Chocolate, milk",
            "category": "RAW",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_update_form = {
            "name": "",
            "category": "PACKAGING",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

    # CRUD functions

    def test_list_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Material ListView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_listview_title)

    def test_list_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Material ListView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:material_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_detail_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Material DetailView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_detailview_title)

    def test_detail_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Material DetailView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:material_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_create_view_successfully_creates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access CreateView (GET) and successfully POST new object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "unit_type")
        cls.assertNotContains(response, "This field is required")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # Test that one additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count + 1)

        # CreateView redirects to detail page of newly-created object
        # So expected_url must incorporate id of newly-created object in order to test response
        new_instance = cls.model.objects.latest("updated_at")
        cls.assertRedirects(
            response,
            reverse("apps.masterdata:material_detail", args=(new_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "added")

    def test_create_view_does_not_create_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST new object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_add")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to CreateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_create_view_does_not_create_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access Material CreateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:material_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_update_view_successfully_updates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access UpdateView (GET) and successfully POST updates to object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "unit_type")
        cls.assertNotContains(response, "This field is required")

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        # # Test that no additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        cls.assertRedirects(
            response,
            reverse("apps.masterdata:material_detail", args=(cls.model_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "updated")

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        cls.assertEqual(cls.model_instance.name, cls.valid_update_form["name"])
        cls.assertEqual(cls.model_instance.category, cls.valid_update_form["category"])

    def test_update_view_does_not_update_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST updates to object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:material_edit", args=(cls.model_instance.id,))

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_update_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to UpdateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        assert cls.model_instance.name != cls.valid_update_form["name"]
        assert cls.model_instance.category != cls.valid_update_form["category"]

    def test_update_view_does_not_update_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access UpdateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:material_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    @classmethod
    def tearDownClass(cls):
        """ cleanup tasks """
        pass


class TestProductViews(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initialize this TestCase """

        super().setUpClass()

        # Create client for handling requests
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        """ Set up data for all tests within this TestCase """

        # Create a user instance for authenticated views
        cls.user = users_models.User.objects.create(
            username=faker.user_name(),
            email=faker.email(),
        )
        cls.user.set_password(faker.password(length=random.randint(12, 24)))
        cls.user.save()

        cls.model = models.Product

        # Product is a proxy model of Item, differentiated on the basis of categories
        # So for the test model instance generation and mutation must constrain the choices
        cls.VALID_CATEGORY_CHOICES = (
            ("WIP", "Work-in-Progress"),
            ("FINISHED", "Finished Product"),
        )

        # Create model instance
        name = "Muffins, blueberry"
        category = "FINISHED"
        cls.model_instance = baker.make(models.Product, name=name, category=category)

        cls.expected_listview_title = "<title>Products</title>"
        cls.expected_detailview_title = f"<title>{cls.model_instance.name}</title>"

        cls.valid_form = {
            "name": "Muffins, lemon-poppyseed",
            "category": "FINISHED",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_form = {
            "name": "",
            "category": "WIP",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        cls.valid_update_form = {
            "name": "Muffins, double chocolate-cream cheese",
            "category": "WIP",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_update_form = {
            "name": "",
            "category": "WIP",
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "state": random.choice(cls.model.STATE_CHOICES)[0],
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

    # CRUD functions

    def test_list_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Product ListView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_listview_title)

    def test_list_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Product ListView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:product_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_detail_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Product DetailView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_detailview_title)

    def test_detail_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Product DetailView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:product_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_create_view_successfully_creates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access CreateView (GET) and successfully POST new object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "unit_type")
        cls.assertNotContains(response, "This field is required")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # Test that one additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count + 1)

        # CreateView redirects to detail page of newly-created object
        # So expected_url must incorporate id of newly-created object in order to test response
        new_instance = cls.model.objects.latest("updated_at")
        cls.assertRedirects(
            response,
            reverse("apps.masterdata:product_detail", args=(new_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "added")

    def test_create_view_does_not_create_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST new object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_add")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to CreateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_create_view_does_not_create_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access Product CreateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:product_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_update_view_successfully_updates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access UpdateView (GET) and successfully POST updates to object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "unit_type")
        cls.assertNotContains(response, "This field is required")

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        # # Test that no additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        cls.assertRedirects(
            response,
            reverse("apps.masterdata:product_detail", args=(cls.model_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "updated")

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        cls.assertEqual(cls.model_instance.name, cls.valid_update_form["name"])
        cls.assertEqual(cls.model_instance.category, cls.valid_update_form["category"])

    def test_update_view_does_not_update_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST updates to object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:product_edit", args=(cls.model_instance.id,))

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_update_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to UpdateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        assert cls.model_instance.name != cls.invalid_update_form["name"]
        assert cls.model_instance.category != cls.invalid_update_form["category"]

    def test_update_view_does_not_update_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access UpdateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:product_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    @classmethod
    def tearDownClass(cls):
        """ cleanup tasks """
        pass


class TestResourceViews(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initialize this TestCase """

        super().setUpClass()

        # Create client for handling requests
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        """ Set up data for all tests within this TestCase """

        # Create a user instance for authenticated views
        cls.user = users_models.User.objects.create(
            username=faker.user_name(),
            email=faker.email(),
        )
        cls.user.set_password(faker.password(length=random.randint(12, 24)))
        cls.user.save()

        cls.model = models.Resource

        # Create model instance
        name = faker.catch_phrase()
        cls.model_instance = baker.make(cls.model, name=name)

        cls.expected_listview_title = "<title>Resources</title>"
        cls.expected_detailview_title = f"<title>{cls.model_instance.name}</title>"

        cls.valid_form = {
            "name": "Mixer, 60 qt",
            "unit": "mixer bowl-minutes",
            "stage": random.choice(cls.model.STAGE_CHOICES)[0],
            "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
            "capacity": random.randint(10, 20),
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_form = {
            "name": "",
            "unit": "mixer bowl-minutes",
            "stage": random.choice(cls.model.STAGE_CHOICES)[0],
            "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
            "capacity": random.randint(10, 20),
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        cls.valid_update_form = {
            "name": "Mixer, 30 qt",
            "unit": "mixer bowl-hours",
            "stage": random.choice(cls.model.STAGE_CHOICES)[0],
            "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
            "capacity": random.randint(10, 20),
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

        # Name is required
        cls.invalid_update_form = {
            "name": "",
            "unit": "mixer bowl-minutes",
            "stage": random.choice(cls.model.STAGE_CHOICES)[0],
            "resource_type": random.choice(cls.model.RESOURCE_TYPE_CHOICES)[0],
            "capacity": random.randint(10, 20),
            "notes": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
        }

    # CRUD functions

    def test_list_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Resource ListView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:resource_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_listview_title)

    def test_list_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Resource ListView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:resource_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_detail_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Resource DetailView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:resource_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_detailview_title)

    def test_detail_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Resource DetailView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:resource_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_create_view_successfully_creates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access CreateView (GET) and successfully POST new object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:resource_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "capacity")
        cls.assertNotContains(response, "This field is required")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # Test that one additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count + 1)

        # CreateView redirects to detail page of newly-created object
        # So expected_url must incorporate id of newly-created object in order to test response
        new_instance = cls.model.objects.latest("updated_at")
        cls.assertRedirects(
            response,
            reverse("apps.masterdata:resource_detail", args=(new_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "added")

    def test_create_view_does_not_create_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST new object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:resource_add")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to CreateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_create_view_does_not_create_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access Resource CreateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:resource_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_update_view_successfully_updates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access UpdateView (GET) and successfully POST updates to object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)
        url = reverse("apps.masterdata:resource_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "capacity")
        cls.assertNotContains(response, "This field is required")

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        # # Test that no additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        cls.assertRedirects(
            response,
            reverse("apps.masterdata:resource_detail", args=(cls.model_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "updated")

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        cls.assertEqual(cls.model_instance.name, cls.valid_update_form["name"])
        cls.assertEqual(cls.model_instance.capacity, cls.valid_update_form["capacity"])

    def test_update_view_does_not_update_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST updates to object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)
        url = reverse("apps.masterdata:resource_edit", args=(cls.model_instance.id,))

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_update_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to UpdateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        # Refresh from database
        cls.model_instance.refresh_from_db()
        assert cls.model_instance.name != cls.invalid_update_form["name"]
        assert cls.model_instance.capacity != cls.invalid_update_form["capacity"]

    def test_update_view_does_not_update_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access UpdateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:resource_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    @classmethod
    def tearDownClass(cls):
        """ cleanup tasks """
        pass


class TestTeamViews(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initialize this TestCase """

        super().setUpClass()

        # Create client for handling requests
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        """ Set up data for all tests within this TestCase """

        # Create a user instance for authenticated views
        cls.user = users_models.User.objects.create(
            username=faker.user_name(),
            email=faker.email(),
        )
        cls.user.set_password(faker.password(length=random.randint(12, 24)))
        cls.user.save()

        cls.model = models.Team

        # Create model instance
        name = "Commissary"
        cls.model_instance = baker.make(models.Team, name=name)

        cls.expected_listview_title = "<title>Teams</title>"
        cls.expected_detailview_title = f"<title>{cls.model_instance.name}</title>"

        cls.valid_form = {
            "name": "Packaging",
            "slug": "",
        }

        # Name is required
        cls.invalid_form = {
            "name": "",
            "slug": "",
        }

        cls.valid_update_form = {
            "name": "Bread",
            "slug": "",
        }

        # Name is required
        cls.invalid_update_form = {
            "name": "",
            "slug": "",
        }

    # CRUD functions

    def test_list_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Team ListView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_listview_title)

    def test_list_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Team ListView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:team_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_detail_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access Team DetailView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_detailview_title)

    def test_detail_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access Team DetailView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:team_detail", args=(cls.model_instance.id,))
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_create_view_successfully_creates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access CreateView (GET) and successfully POST new object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "slug")
        cls.assertNotContains(response, "This field is required")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # Test that one additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count + 1)

        # CreateView redirects to detail page of newly-created object
        # So expected_url must incorporate id of newly-created object in order to test response
        new_instance = cls.model.objects.latest("updated_at")
        cls.assertRedirects(
            response,
            reverse("apps.masterdata:team_detail", args=(new_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "added")

    def test_create_view_does_not_create_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST new object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_add")

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to CreateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_create_view_does_not_create_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access Team CreateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:team_add")

        # Test CreateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test CreateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_form, enforce_csrf_checks=True, follow=True
        )

        # cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    def test_update_view_successfully_updates_object_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should be able to access UpdateView (GET) and successfully POST updates to object """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertTemplateUsed("/template/generic/generic_mutate.html")
        cls.assertContains(response, "name")
        cls.assertContains(response, "slug")
        cls.assertNotContains(response, "This field is required")

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        # # Test that no additional object has been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        cls.assertRedirects(
            response,
            reverse("apps.masterdata:team_detail", args=(cls.model_instance.id,)),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        cls.assertContains(response, "updated")

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        cls.assertEqual(cls.model_instance.name, cls.valid_update_form["name"])

    def test_update_view_does_not_update_object_with_invalid_input_when_called_by_authenticated_user(
        cls,
    ):
        """ Authenticated users should not be able to successfully POST updates to object with invalid or missing form values """

        prior_objects_count = cls.model.objects.count()

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:team_edit", args=(cls.model_instance.id,))

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.invalid_update_form, enforce_csrf_checks=True, follow=True
        )

        # Response should have returned to UpdateView url, displaying form errors
        cls.assertContains(response, "This field is required")

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

        # Refresh from Db
        cls.model_instance.refresh_from_db()
        assert cls.model_instance.name != cls.valid_update_form["name"]

    def test_update_view_does_not_update_object_when_called_by_anonymous_user(
        cls,
    ):
        """ Anonymous users should not be able to access UpdateView (GET or POST) and should be redirected to login """

        prior_objects_count = cls.model.objects.count()

        cls.client.logout()

        url = reverse("apps.masterdata:team_edit", args=(cls.model_instance.id,))

        # Test UpdateView form (via GET)
        response = cls.client.get(url, enforce_csrf_checks=True, follow=True)
        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test UpdateView action (via POST)
        response = cls.client.post(
            url, data=cls.valid_update_form, enforce_csrf_checks=True, follow=True
        )

        cls.assertRedirects(
            response,
            f"/login/?next={url}",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Test that no additional objects have been created
        cls.assertEqual(cls.model.objects.count(), prior_objects_count)

    @classmethod
    def tearDownClass(cls):
        """ cleanup tasks """
        pass


class TestUnitMeasurementViews(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Initialize this TestCase """

        super().setUpClass()

        # Create client for handling requests
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        """ Set up data for all tests within this TestCase """

        # Create a user instance for authenticated views
        cls.user = users_models.User.objects.create(
            username=faker.user_name(),
            email=faker.email(),
        )
        cls.user.set_password(faker.password(length=random.randint(12, 24)))
        cls.user.save()

        cls.model = models.UnitMeasurement

        # Create model instance
        name = "kilogram(s)"
        cls.model_instance = baker.make(cls.model, name=name)

        cls.expected_listview_title = "<title>Unit Measurements</title>"
        cls.expected_detailview_title = f"<title>{cls.model_instance.name}</title>"

        cls.valid_form = {
            "name": "kilogram(s)",
            "symbol": "kg",
            "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "display_quantity_smallest": 0.125,
            "display_quantity_largest": 1000,
        }

        # Name is required
        cls.invalid_form = {
            "name": "",
            "symbol": "kg",
            "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "display_quantity_smallest": 0.125,
            "display_quantity_largest": 1000,
        }

        cls.valid_update_form = {
            "name": "gram(s)",
            "symbol": "g",
            "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "display_quantity_smallest": 0.125,
            "display_quantity_largest": 1000,
        }

        # Name is required
        cls.invalid_update_form = {
            "name": "",
            "symbol": "kg",
            "unit_system": random.choice(cls.model.UNIT_SYSTEM_CHOICES)[0],
            "unit_type": random.choice(cls.model.UNIT_TYPE_CHOICES)[0],
            "display_quantity_smallest": 0.125,
            "display_quantity_largest": 1000,
        }

    # CRUD functions

    def test_list_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access UnitMeasurement ListView """

        cls.client.force_login(cls.user)

        url = reverse("apps.masterdata:unitmeasurement_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_listview_title)

    def test_list_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access UnitMeasurement ListView and should be redirected to login """

        cls.client.logout()

        url = reverse("apps.masterdata:unitmeasurement_list")
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    def test_detail_view_can_be_viewed_by_authenticated_user(cls):
        """ Authenticated users should be able to access UnitMeasurement DetailView """

        cls.client.force_login(cls.user)

        url = reverse(
            "apps.masterdata:unitmeasurement_detail", args=(cls.model_instance.id,)
        )
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 200)
        cls.assertContains(response, cls.expected_detailview_title)

    def test_detail_view_cannot_be_viewed_by_anonymous_user(cls):
        """ Anonymous users should not be able to access UnitMeasurement DetailView and should be redirected to login """

        cls.client.logout()

        url = reverse(
            "apps.masterdata:unitmeasurement_detail", args=(cls.model_instance.id,)
        )
        response = cls.client.get(url)

        cls.assertEqual(response.status_code, 302)
        cls.assertRedirects(response, f"/login/?next={url}")

    @classmethod
    def tearDownClass(cls):
        """ cleanup tasks """
        pass

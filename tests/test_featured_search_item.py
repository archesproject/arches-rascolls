from django.contrib.auth.models import User
from django.test import TestCase

from arches_search.models.models import SavedSearch

from arches_rascolls.admin import FeaturedSearchItemForm
from arches_rascolls.models import FeaturedSearchItem

SAMPLE_QUERY = {"groups": [{"op": "and", "clauses": []}]}
SAMPLE_PRESENTATION = {"icon": "pi-palette", "color": "#0d9488"}


class FeaturedSearchItemTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(
            username="curator", password="password123", is_staff=True
        )
        cls.regular_user = User.objects.create_user(
            username="regular", password="password123"
        )
        cls.staff_search = SavedSearch.objects.create(
            name="Paint References",
            description="Paint reference and sample items",
            query_definition=SAMPLE_QUERY,
            creator=cls.staff_user,
        )

    # --- display_label / display_description fallback ---

    def test_display_label_falls_back_to_saved_search_name_when_absent(self):
        item = FeaturedSearchItem.objects.create(
            saved_search=self.staff_search,
            presentation={"icon": "pi-palette", "color": "#0d9488"},
        )

        self.assertEqual(item.display_label, self.staff_search.name)

    def test_display_description_falls_back_to_saved_search_description_when_absent(
        self,
    ):
        item = FeaturedSearchItem.objects.create(
            saved_search=self.staff_search,
            presentation={"icon": "pi-palette", "color": "#0d9488"},
        )

        self.assertEqual(item.display_description, self.staff_search.description)

    # --- FeaturedSearchItemForm curation constraints ---

    def test_saved_search_field_excludes_non_staff_authored_searches(self):
        non_staff_search = SavedSearch.objects.create(
            name="Regular User's Search",
            query_definition=SAMPLE_QUERY,
            creator=self.regular_user,
        )

        form = FeaturedSearchItemForm()
        selectable_ids = set(
            form.fields["saved_search"].queryset.values_list("pk", flat=True)
        )

        self.assertIn(self.staff_search.pk, selectable_ids)
        self.assertNotIn(non_staff_search.pk, selectable_ids)

    def test_form_rejects_saved_search_with_no_terms_or_groups(self):
        non_dynamic_search = SavedSearch.objects.create(
            name="Non-dynamic Search",
            query_definition={"snapshot": True},
            creator=self.staff_user,
        )

        form = FeaturedSearchItemForm(
            data={
                "saved_search": non_dynamic_search.pk,
                "presentation": SAMPLE_PRESENTATION,
                "sort_order": 0,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_accepts_saved_search_with_terms_or_groups(self):
        form = FeaturedSearchItemForm(
            data={
                "saved_search": self.staff_search.pk,
                "presentation": SAMPLE_PRESENTATION,
                "sort_order": 0,
                "is_active": True,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_invalid_icon(self):
        form = FeaturedSearchItemForm(
            data={
                "saved_search": self.staff_search.pk,
                "presentation": {"icon": "not-a-primeicon", "color": "#0d9488"},
                "sort_order": 0,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_rejects_non_object_presentation(self):
        form = FeaturedSearchItemForm(
            data={
                "saved_search": self.staff_search.pk,
                "presentation": ["pi-palette", "#0d9488"],
                "sort_order": 0,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_color(self):
        form = FeaturedSearchItemForm(
            data={
                "saved_search": self.staff_search.pk,
                "presentation": {"icon": "pi-palette", "color": "teal"},
                "sort_order": 0,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())

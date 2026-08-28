from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from arches_search.models.models import SavedSearch

from arches_rascolls.models import FeaturedSearchItem

SAMPLE_QUERY = {"groups": [{"op": "and", "clauses": []}]}


class FeaturedItemsAPITest(TestCase):
    def test_get_returns_active_items_in_the_expected_shape(self):
        staff_user = User.objects.create_user(
            username="curator", password="password123", is_staff=True
        )
        saved_search = SavedSearch.objects.create(
            name="Paint References",
            description="Paint reference and sample items",
            query_definition=SAMPLE_QUERY,
            creator=staff_user,
        )
        active_item = FeaturedSearchItem.objects.create(
            saved_search=saved_search,
            presentation={
                "label": "Custom Label",
                "description": "Custom description",
                "icon": "pi-palette",
                "color": "#0d9488",
            },
            is_active=True,
        )
        FeaturedSearchItem.objects.create(
            saved_search=saved_search,
            presentation={"icon": "pi-palette", "color": "#0d9488"},
            is_active=False,
        )

        response = self.client.get(reverse("api-featured-items"))

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(
            [result["id"] for result in results],
            [str(active_item.featuredsearchitemid)],
        )
        result = results[0]
        self.assertEqual(result["label"], "Custom Label")
        self.assertEqual(result["description"], "Custom description")
        self.assertEqual(result["icon"], "pi-palette")
        self.assertEqual(result["color"], "#0d9488")
        self.assertEqual(result["search_definition"], saved_search.query_definition)

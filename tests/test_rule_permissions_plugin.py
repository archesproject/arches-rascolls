from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from arches.app.models.models import Plugin

RULE_PERMISSIONS_SLUG = "rule-permissions"


class RulePermissionsPluginTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="abac_superuser", password="Test12345!"
        )
        self.user = User.objects.create_user(
            username="abac_user", password="Test12345!"
        )

    def test_plugin_is_registered_and_shown(self):
        plugin = Plugin.objects.get(slug=RULE_PERMISSIONS_SLUG)
        self.assertTrue(plugin.config["show"])

    def test_superuser_can_view_plugin(self):
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("plugins", kwargs={"slug": RULE_PERMISSIONS_SLUG}),
            {"json": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slug"], RULE_PERMISSIONS_SLUG)

    def test_superuser_sees_plugin_in_plugin_list(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("api_plugins"))

        slugs = [plugin["slug"] for plugin in response.json()]
        self.assertIn(RULE_PERMISSIONS_SLUG, slugs)

    def test_non_superuser_cannot_view_plugin(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("plugins", kwargs={"slug": RULE_PERMISSIONS_SLUG}),
            {"json": "true"},
        )

        self.assertEqual(response.status_code, 302)

    def test_rule_api_is_routed_and_superuser_only(self):
        self.client.force_login(self.superuser)
        self.assertEqual(self.client.get(reverse("abac_rules")).status_code, 200)

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("abac_rules")).status_code, 403)

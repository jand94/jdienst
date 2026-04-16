from django.test import SimpleTestCase


class SmokeTest(SimpleTestCase):
    """Verifies that the Django project boots and core settings are valid."""

    def test_installed_apps_not_empty(self):
        from django.conf import settings

        self.assertTrue(len(settings.INSTALLED_APPS) > 0)

    def test_root_urlconf_set(self):
        from django.conf import settings

        self.assertEqual(settings.ROOT_URLCONF, "backend.urls")

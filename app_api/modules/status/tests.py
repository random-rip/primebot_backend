from django.test import TestCase
from rest_framework.test import APIRequestFactory

from app_api.modules.status.views import StatusView


class StatusTest(TestCase):
    databases = []

    def test_gitlab(self):
        request = APIRequestFactory().get("/api/status")
        response = StatusView.as_view()(request, )

        expected = {
            "version": "v1.18.1",
            "latest_changes": "",
            "prime_league": True,
            "discord": True,
            "telegram": True,
        }
        print(response.data)
        self.assertDictEqual(response.data, expected)

from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from app_api.modules.status.views import StatusView


class StatusTest(TestCase):
    databases = []

    def test_gitlab(self):
        request = APIRequestFactory().get("/api/status")
        response = StatusView.as_view()(request, )

        expected = {
            "version": "v2.1",
            "latest_changes": "- Change 1\r\n- Change 2",
            "prime_league": True,
            "discord": None,
            "telegram": None,
        }

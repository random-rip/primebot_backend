from django.test import TestCase

from core.parsing.logs import BaseLog, LogSchedulingConfirmation, LogSchedulingReset


class TestLogParsing(TestCase):
    databases = []

    def test_scheduling_reset(self):
        log = BaseLog.return_specified_log("1231231231", "", "scheduling_confirm", "")

        self.assertIsInstance(log, LogSchedulingReset)

    def test_scheduling_confirmation(self):
        log = BaseLog.return_specified_log("1231231231", "", "scheduling_confirm", "Tue, 28 Oct 2025 19:30:00 +0100")

        self.assertIsInstance(log, LogSchedulingConfirmation)

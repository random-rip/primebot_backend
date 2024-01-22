from datetime import datetime
from unittest import mock

from django.test import TestCase

from app_prime_league.management.commands.updates_between_calibration_and_group_stage import (
    Command as UpdatesBetweenCalibrationAndGroupStage,
)
from app_prime_league.management.commands.updates_between_splits import Command as UpdatesBetweenSplits
from app_prime_league.management.commands.updates_in_calibration_stage import Command as UpdatesInCalibrationStage
from app_prime_league.management.commands.updates_in_group_stage_and_playoffs import (
    Command as UpdatesInGroupStageAndPlayoffs,
)
from core.test_utils import CompareModelObjectsMixin, SplitBuilder


class UpdateDependencyTest(TestCase, CompareModelObjectsMixin):
    @classmethod
    def setUpTestData(cls):
        SplitBuilder().build()

    def test_updates_between_splits(self):
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 19)
            self.assertFalse(UpdatesBetweenSplits.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 20)
            self.assertTrue(UpdatesBetweenSplits.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 21)
            self.assertTrue(UpdatesBetweenSplits.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 29)  # split not ended, last playoff day
            self.assertTrue(UpdatesBetweenSplits.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 30)  # split ended
            self.assertFalse(UpdatesBetweenSplits.is_time_exceeded())

    def test_updates_in_calibration_stage(self):
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 20)
            self.assertFalse(UpdatesInCalibrationStage.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 21)
            self.assertFalse(UpdatesInCalibrationStage.is_time_exceeded())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 22)
            self.assertTrue(UpdatesInCalibrationStage.is_time_exceeded())

    def test_updates_between_calibration_and_group_stage(self):
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 24)
            self.assertFalse(UpdatesBetweenCalibrationAndGroupStage.is_time_exceeded())
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 25)
            self.assertTrue(UpdatesBetweenCalibrationAndGroupStage.is_time_exceeded())

    def test_updates_in_group_stage_and_playoffs(self):
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 28)
            self.assertFalse(UpdatesInGroupStageAndPlayoffs.is_time_exceeded())
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 29)
            self.assertFalse(UpdatesInGroupStageAndPlayoffs.is_time_exceeded())
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 30)
            self.assertTrue(UpdatesInGroupStageAndPlayoffs.is_time_exceeded())

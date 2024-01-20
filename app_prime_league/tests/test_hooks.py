from datetime import datetime
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import make_aware
from django_q.models import Schedule

from app_prime_league.management.commands.updates_between_calibration_and_group_stage import (
    activate_updates_in_group_stage_and_playoffs,
)
from app_prime_league.management.commands.updates_between_splits import activate_updates_in_calibration_stage
from app_prime_league.management.commands.updates_in_calibration_stage import (
    activate_updates_between_calibration_and_group_stage,
)
from app_prime_league.management.commands.updates_in_group_stage_and_playoffs import activate_updates_between_splits
from core.test_utils import CompareModelObjectsMixin, SplitBuilder


class HookTests(TestCase, CompareModelObjectsMixin):
    def test_updates_between_splits(self):
        SplitBuilder().build()
        activate_updates_between_splits(mock.Mock(success=False))
        self.assertEqual(0, Schedule.objects.filter(name="Updates between splits").count())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 4, 29)
            activate_updates_between_splits(mock.Mock(success=True))
        self.assertEqual(0, Schedule.objects.filter(name="Updates between splits").count())

    def test_updates_between_splits_with_success(self):
        SplitBuilder().build()
        call_command("updates_in_group_stage_and_playoffs", "--schedule")
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 4, 30))
            activate_updates_between_splits(mock.Mock(success=True))
        self.assertEqual(1, Schedule.objects.filter(name="Updates between splits").count())

    def test_calibration_stage(self):
        SplitBuilder().build()
        activate_updates_in_calibration_stage(mock.Mock(success=False))
        self.assertEqual(0, Schedule.objects.filter(name="Update Teams and Matches in Calibration Stage").count())

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(2024, 1, 19)
            activate_updates_between_splits(mock.Mock(success=True))
        self.assertEqual(0, Schedule.objects.filter(name="Update Teams and Matches in Calibration Stage").count())

    def test_calibration_stage_with_success(self):
        SplitBuilder().build()
        call_command("updates_between_splits", "--schedule")
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 1, 20))
            activate_updates_in_calibration_stage(mock.Mock(success=True))
        self.assertEqual(1, Schedule.objects.filter(name="Update Teams and Matches in Calibration Stage").count())

    def test_updates_between_calibration_and_group_stage(self):
        SplitBuilder().build()
        activate_updates_between_calibration_and_group_stage(mock.Mock(success=False))
        self.assertEqual(
            0, Schedule.objects.filter(name="Update Teams and Matches between Calibration and Group Stage").count()
        )

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 1, 20))
            activate_updates_between_calibration_and_group_stage(mock.Mock(success=True))
        self.assertEqual(
            0, Schedule.objects.filter(name="Update Teams and Matches between Calibration and Group Stage").count()
        )

    def test_updates_between_calibration_and_group_stage_with_success(self):
        SplitBuilder().build()
        call_command("updates_in_calibration_stage", "--schedule")
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 1, 21))
            activate_updates_between_calibration_and_group_stage(mock.Mock(success=True))
        self.assertEqual(
            1, Schedule.objects.filter(name="Update Teams and Matches between Calibration and Group Stage").count()
        )

    def test_updates_in_group_stage_and_playoffs(self):
        SplitBuilder().build()
        activate_updates_in_group_stage_and_playoffs(mock.Mock(success=False))
        self.assertEqual(
            0, Schedule.objects.filter(name="Update Teams and Matches in Group Stage and Playoffs").count()
        )

        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 1, 24))
            activate_updates_in_group_stage_and_playoffs(mock.Mock(success=True))
        self.assertEqual(
            0, Schedule.objects.filter(name="Update Teams and Matches in Group Stage and Playoffs").count()
        )

    def test_updates_in_group_stage_and_playoffs_with_success(self):
        SplitBuilder().build()
        call_command("updates_between_calibration_and_group_stage", "--schedule")
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 1, 25))
            activate_updates_in_group_stage_and_playoffs(mock.Mock(success=True))
        self.assertEqual(
            1, Schedule.objects.filter(name="Update Teams and Matches in Group Stage and Playoffs").count()
        )

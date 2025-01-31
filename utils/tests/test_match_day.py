from datetime import date, datetime
from unittest import mock

from django.test import TestCase
from django.utils.timezone import make_aware

from app_prime_league.factories import SplitFactory
from utils.utils import count_weeks


class MatchDayTest(TestCase):
    @mock.patch('django.utils.timezone.now')
    def test_current(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2024, 3, 25))  # Monday Week 9
        split = SplitFactory(group_stage_start=date(2024, 1, 25))
        match_day = split.get_current_match_day()
        self.assertEqual(9, match_day)

    def test_calibration(self):
        split_start = datetime(2022, 8, 1)
        current = datetime(2022, 7, 22)
        match_day = count_weeks(split_start, current)
        self.assertEqual(-1, match_day)

    def test_week_between_calibration_and_group_stage(self):
        split_start = datetime(2022, 8, 1)
        current = datetime(2022, 7, 25)
        match_day = count_weeks(split_start, current)
        self.assertEqual(0, match_day)

    def test_group_stage(self):
        split_start = datetime(2022, 8, 1)
        self.assertEqual(1, count_weeks(split_start, datetime(2022, 8, 1)))
        self.assertEqual(2, count_weeks(split_start, datetime(2022, 8, 8)))
        self.assertEqual(3, count_weeks(split_start, datetime(2022, 8, 15)))
        self.assertEqual(4, count_weeks(split_start, datetime(2022, 8, 22)))
        self.assertEqual(5, count_weeks(split_start, datetime(2022, 8, 29)))
        self.assertEqual(6, count_weeks(split_start, datetime(2022, 9, 5)))
        self.assertEqual(7, count_weeks(split_start, datetime(2022, 9, 12)))
        self.assertEqual(8, count_weeks(split_start, datetime(2022, 9, 19)))

    def test_tiebreaker(self):
        split_start = datetime(2022, 8, 1)
        self.assertEqual(9, count_weeks(split_start, datetime(2022, 9, 26)))

    def test_playoffs(self):
        split_start = datetime(2022, 8, 1)
        self.assertEqual(10, count_weeks(split_start, datetime(2022, 10, 3)))

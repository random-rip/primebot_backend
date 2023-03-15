from datetime import datetime
from unittest import mock

import pytz
from django.conf import settings
from django.test import TestCase

from app_prime_league.models import Team, Match


class MatchesTest(TestCase):

    def setUp(self):
        self.team_a = Team.objects.create(id=1, name="Team A", team_tag="TA")
        self.split_start = datetime(2022, 6, 6).astimezone(pytz.timezone(settings.TIME_ZONE))
        # calibration
        Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_GROUP, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=2, match_day=2, match_type=Match.MATCH_TYPE_GROUP, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=3, match_day=3, match_type=Match.MATCH_TYPE_GROUP, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=4, match_day=4, match_type=Match.MATCH_TYPE_GROUP, team=self.team_a,
                             has_side_choice=True, )

        # group phase
        Match.objects.create(match_id=10, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=20, match_day=2, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=30, match_day=3, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team_a,
                             has_side_choice=True, )
        Match.objects.create(match_id=40, match_day=4, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team_a,
                             has_side_choice=True, )

        # tiebreaker
        Match.objects.create(match_id=100, match_day=Match.MATCH_DAY_TIEBREAKER, match_type=Match.MATCH_TYPE_LEAGUE,
                             team=self.team_a, has_side_choice=True, )
        Match.objects.create(match_id=200, match_day=Match.MATCH_DAY_TIEBREAKER, match_type=Match.MATCH_TYPE_LEAGUE,
                             team=self.team_a, has_side_choice=True, )
        Match.objects.create(match_id=300, match_day=Match.MATCH_DAY_TIEBREAKER, match_type=Match.MATCH_TYPE_LEAGUE,
                             team=self.team_a, has_side_choice=True, )

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_calibration(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 5, 28))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([1], result)

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_week_between_calibration_and_group_stage(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 5, 30))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_group_stage(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 6, 6))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)

        timezone_mock.now = mock.Mock(return_value=datetime(2022, 6, 13))
        result = list(self.team_a.get_obvious_matches_based_on_stage(2).values_list("match_id", flat=True))
        self.assertListEqual([20], result)

        timezone_mock.now = mock.Mock(return_value=datetime(2022, 6, 20))
        result = list(self.team_a.get_obvious_matches_based_on_stage(3).values_list("match_id", flat=True))
        self.assertListEqual([30], result)

        timezone_mock.now = mock.Mock(return_value=datetime(2022, 6, 27))
        result = list(self.team_a.get_obvious_matches_based_on_stage(4).values_list("match_id", flat=True))
        self.assertListEqual([40], result)

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_group_stage(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 7, 25))
        result = list(self.team_a.get_obvious_matches_based_on_stage(99).values_list("match_id", flat=True))
        self.assertListEqual([100, 200, 300], result)

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_no_playoffs(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 8, 1))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)

    @mock.patch('utils.utils.timezone')
    @mock.patch('utils.utils.settings')
    def test_playoffs(self, settings, timezone_mock):
        settings.CURRENT_SPLIT_START = self.split_start
        timezone_mock.now = mock.Mock(return_value=datetime(2022, 8, 1))
        # Playoffs
        Match.objects.create(match_id=1000, match_day=Match.MATCH_DAY_PLAYOFF, match_type=Match.MATCH_TYPE_PLAYOFF,
                             team=self.team_a, has_side_choice=True, )
        Match.objects.create(match_id=2000, match_day=Match.MATCH_DAY_PLAYOFF, match_type=Match.MATCH_TYPE_PLAYOFF,
                             team=self.team_a, has_side_choice=True, )
        Match.objects.create(match_id=3000, match_day=Match.MATCH_DAY_PLAYOFF, match_type=Match.MATCH_TYPE_PLAYOFF,
                             team=self.team_a, has_side_choice=True, )

        result = list(self.team_a.get_obvious_matches_based_on_stage(0).values_list("match_id", flat=True))
        self.assertListEqual([1000, 2000, 3000], result)

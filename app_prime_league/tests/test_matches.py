from datetime import date, datetime
from unittest import mock

from django.test import TestCase
from django.utils.timezone import make_aware

from app_prime_league.factories import MatchFactory, SplitFactory, TeamFactory
from app_prime_league.models import Match


class MatchesTest(TestCase):
    def setUp(self):
        self.team_a = TeamFactory(name="Team A", team_tag="TA")
        SplitFactory.from_registration_dates(date(2022, 5, 19), date(2022, 6, 1))
        # calibration
        MatchFactory(
            match_id=1,
            match_day=1,
            match_type=Match.MATCH_TYPE_GROUP,
            team=self.team_a,
        )
        MatchFactory(
            match_id=2,
            match_day=2,
            match_type=Match.MATCH_TYPE_GROUP,
            team=self.team_a,
        )
        MatchFactory(
            match_id=3,
            match_day=3,
            match_type=Match.MATCH_TYPE_GROUP,
            team=self.team_a,
        )
        MatchFactory(
            match_id=4,
            match_day=4,
            match_type=Match.MATCH_TYPE_GROUP,
            team=self.team_a,
        )

        # group phase
        MatchFactory(
            match_id=10,
            match_day=1,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )
        MatchFactory(
            match_id=20,
            match_day=2,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )
        MatchFactory(
            match_id=30,
            match_day=3,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )
        MatchFactory(
            match_id=40,
            match_day=4,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )

        # tiebreaker
        MatchFactory(
            match_id=100,
            match_day=Match.MATCH_DAY_TIEBREAKER,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )
        MatchFactory(
            match_id=200,
            match_day=Match.MATCH_DAY_TIEBREAKER,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )
        MatchFactory(
            match_id=300,
            match_day=Match.MATCH_DAY_TIEBREAKER,
            match_type=Match.MATCH_TYPE_LEAGUE,
            team=self.team_a,
        )

    @mock.patch('django.utils.timezone.now')
    def test_calibration(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 5, 28))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([1], result)

    @mock.patch('django.utils.timezone.now')
    def test_week_between_calibration_and_group_stage(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 5, 30))  # Monday
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([1], result)

        timezone_mock.return_value = make_aware(datetime(2022, 5, 31))  # Tuesday
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([1], result)

        timezone_mock.return_value = make_aware(datetime(2022, 6, 1))  # Wednesday
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([1], result)

        timezone_mock.return_value = make_aware(datetime(2022, 6, 2))  # Thursday
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)  # first group stage match. Groups will be built on thursday

    @mock.patch('django.utils.timezone.now')
    def test_group_stage(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 6, 6))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)

        timezone_mock.return_value = make_aware(datetime(2022, 6, 13))
        result = list(self.team_a.get_obvious_matches_based_on_stage(2).values_list("match_id", flat=True))
        self.assertListEqual([20], result)

        timezone_mock.return_value = make_aware(datetime(2022, 6, 20))
        result = list(self.team_a.get_obvious_matches_based_on_stage(3).values_list("match_id", flat=True))
        self.assertListEqual([30], result)

        timezone_mock.return_value = make_aware(datetime(2022, 6, 27))
        result = list(self.team_a.get_obvious_matches_based_on_stage(4).values_list("match_id", flat=True))
        self.assertListEqual([40], result)

    @mock.patch('django.utils.timezone.now')
    def test_group_stage_2(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 7, 25))
        result = list(
            self.team_a.get_obvious_matches_based_on_stage(99).order_by("match_id").values_list("match_id", flat=True)
        )
        self.assertListEqual([100, 200, 300], result)

    @mock.patch('django.utils.timezone.now')
    def test_no_playoffs(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 8, 1))
        result = list(self.team_a.get_obvious_matches_based_on_stage(1).values_list("match_id", flat=True))
        self.assertListEqual([10], result)

    @mock.patch('django.utils.timezone.now')
    def test_playoffs(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 8, 21))
        # Playoffs start on 2022-08-21
        MatchFactory(match_id=1000, team=self.team_a, match_type=Match.MATCH_TYPE_PLAYOFF, match_day=0)
        MatchFactory(match_id=2000, team=self.team_a, match_type=Match.MATCH_TYPE_PLAYOFF, match_day=0)
        MatchFactory(match_id=3000, team=self.team_a, match_type=Match.MATCH_TYPE_PLAYOFF, match_day=0)

        result = list(self.team_a.get_obvious_matches_based_on_stage(0).values_list("match_id", flat=True))
        self.assertListEqual([1000, 2000, 3000], result)

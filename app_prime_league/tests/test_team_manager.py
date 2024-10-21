from datetime import datetime
from unittest import mock

from django.test import TestCase
from django.utils.timezone import make_aware

from app_prime_league.models import Team
from core.test_utils import CompareModelObjectsMixin, MatchBuilder, SplitBuilder, TeamBuilder


class GetRegisteredTeamsTest(TestCase, CompareModelObjectsMixin):
    def test_registered_teams(self):
        TeamBuilder("Team unregistered").build()
        TeamBuilder("Team Telegram registered").set_telegram(1).build()
        TeamBuilder("Team Discord registered").set_discord(1).build()

        result = Team.objects.get_registered_teams().order_by("name")

        expected = [
            {"name": "Team Discord registered"},
            {"name": "Team Telegram registered"},
        ]

        self.assertModelObjectsListEqual(expected, result)


class GetTeamsToUpdateTest(TestCase, CompareModelObjectsMixin):
    def setUp(self):
        self.split = SplitBuilder().build()
        self.team = TeamBuilder("Team registered").set_discord(1).build()
        self.enemy_team = TeamBuilder("Team Enemy").build()
        TeamBuilder("Team C").build()

    def test_simple(self):
        MatchBuilder(1, team_1=self.team).set_team_2(self.enemy_team).build()
        result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
            {"name": "Team Enemy"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match(self):
        MatchBuilder(1, team_1=self.team).set_team_2(self.enemy_team).set_closed().build()
        result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match_with_begin_greater_two_days_after(self):
        MatchBuilder(1, team_1=self.team).set_team_2(self.enemy_team).set_closed().set_match_day(1).build()
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 2, 7))
            result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match_with_begin_within_two_days_after(self):
        MatchBuilder(1, team_1=self.team).set_team_2(self.enemy_team).set_closed().set_match_day(1).build()
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 2, 6))
            result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
            {"name": "Team Enemy"},
        ]
        self.assertModelObjectsListEqual(expected, result)


class CurrentSplitTeamManagerTest(TestCase, CompareModelObjectsMixin):
    def test_current_split(self):
        SplitBuilder().build()
        TeamBuilder("Team A").build()
        TeamBuilder("Team B").current_split().build()

        result = Team.current_split_objects.all()

        expected = [
            {"name": "Team B"},
        ]
        self.assertModelObjectsListEqual(expected, result)

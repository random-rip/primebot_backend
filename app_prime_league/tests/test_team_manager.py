from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.utils.timezone import make_aware

from app_prime_league.factories import ChannelFactory, MatchFactory, SplitFactory, TeamFactory
from app_prime_league.models import ChannelTeam, Match, Team
from app_prime_league.models.channel import Platforms
from core.test_utils import CompareModelObjectsMixin


class GetRegisteredTeamsTest(TestCase, CompareModelObjectsMixin):
    def test_registered_teams(self):
        TeamFactory(name="Team unregistered")
        TeamFactory(name="Team Telegram registered", channels=[ChannelFactory(platform=Platforms.TELEGRAM)])
        TeamFactory(name="Team Discord registered", channels=[ChannelFactory(platform=Platforms.DISCORD)])

        result = Team.objects.get_registered_teams().order_by("name")

        expected = [
            {"name": "Team Discord registered"},
            {"name": "Team Telegram registered"},
        ]

        self.assertModelObjectsListEqual(expected, result)


class GetTeamsToUpdateTest(TestCase, CompareModelObjectsMixin):
    def setUp(self):
        self.split = SplitFactory()
        self.team = TeamFactory(name="Team registered", channels=[ChannelFactory(platform=Platforms.DISCORD)])
        self.enemy_team = TeamFactory(name="Team Enemy")
        TeamFactory()

    def test_simple(self):
        MatchFactory(team=self.team, enemy_team=self.enemy_team)
        result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
            {"name": "Team Enemy"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match(self):
        MatchFactory(team=self.team, enemy_team=self.enemy_team, closed=True)
        result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match_with_begin_greater_two_days_after(self):
        MatchFactory(
            team=self.team, enemy_team=self.enemy_team, closed=True, begin=datetime(2024, 2, 4, tzinfo=ZoneInfo("UTC"))
        )
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2024, 2, 7))
            result = Team.objects.get_teams_to_update().order_by("id")
        expected = [
            {"name": "Team registered"},
        ]
        self.assertModelObjectsListEqual(expected, result)

    def test_closed_match_with_begin_within_two_days_after(self):
        MatchFactory(
            team=self.team, enemy_team=self.enemy_team, closed=True, begin=datetime(2024, 2, 4, tzinfo=ZoneInfo("UTC"))
        )
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
        TeamFactory(name="Team A")
        TeamFactory(name="Team B", split=SplitFactory())

        result = Team.current_split_objects.all()

        expected = [
            {"name": "Team B"},
        ]
        self.assertModelObjectsListEqual(expected, result)


class SoftDeleteTests(TestCase, CompareModelObjectsMixin):

    def test_simple(self):
        team = TeamFactory(name="Delete me")
        MatchFactory(team=team, enemy_team=None)
        TeamFactory(name="Dont delete me")

        Team.objects.soft_delete(team)

        expected = [
            {"name": "Dont delete me"},
        ]
        self.assertModelObjectsListEqual(expected, Team.objects.all())
        self.assertEqual(Match.objects.count(), 0)

    def test_delete_matches(self):
        team = TeamFactory(name="Delete me")
        MatchFactory(team=team, enemy_team=None)

        Team.objects.soft_delete(team)

        self.assertEqual(Match.objects.count(), 0)

    def test_team_has_channels(self):
        team = TeamFactory(channels=[ChannelFactory()])

        Team.objects.soft_delete(team)

        self.assertEqual(Team.objects.count(), 1)

    def test_team_is_only_enemy_team_with_matches(self):
        team = TeamFactory()
        match1 = MatchFactory(team=TeamFactory(), enemy_team=team)

        Team.objects.soft_delete(team)

        self.assertEqual(Team.objects.count(), 2)
        self.assertEqual(Match.objects.count(), 1)
        self.assertEqual(match1, Match.objects.first())

    def test_team_is_only_team_with_matches(self):
        team = TeamFactory()
        MatchFactory(team=team, enemy_team=TeamFactory())

        result = Team.objects.soft_delete(team)
        self.assertTrue(result)
        self.assertEqual(Team.objects.count(), 1)

    def test_multiple(self):
        team1 = TeamFactory()
        team2 = TeamFactory()
        MatchFactory(team=team1, enemy_team=None)
        MatchFactory(team=team2, enemy_team=None)

        Team.objects.soft_delete_multiple([team1, team2])

        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(Match.objects.count(), 0)

    def test_cleanup(self):
        team = TeamFactory(name="Delete me", channels=[ChannelFactory()])
        team2 = TeamFactory(name="Related team")
        MatchFactory(team=team, enemy_team=team2)
        team3 = TeamFactory(name="But not me")
        MatchFactory(team=team3, enemy_team=None)
        team4 = TeamFactory(name="Also not me", channels=[ChannelFactory()])
        MatchFactory(team=team, enemy_team=team4)
        team5 = TeamFactory(name="Also not me because i have other matches")
        MatchFactory(team=team, enemy_team=team5)
        MatchFactory(team=team3, enemy_team=team5)

        result = Team.objects.cleanup(team.channel_teams.first())
        self.assertListEqual(["Delete me", "Related team"], result)
        self.assertModelObjectsListEqual(
            [
                {"name": "Also not me"},
                {"name": "Also not me because i have other matches"},
                {"name": "But not me"},
            ],
            Team.objects.order_by("name"),
        )
        self.assertEqual(Match.objects.count(), 2)

    def test_cleanup_multiple(self):
        team = TeamFactory(name="Delete me", channels=[ChannelFactory()])
        team2 = TeamFactory(name="Related team")
        MatchFactory(team=team, enemy_team=team2)
        team3 = TeamFactory(name="Delete me 2", channels=[ChannelFactory()])
        MatchFactory(team=team3, enemy_team=None)
        team4 = TeamFactory(name="Not me", channels=[ChannelFactory()])
        MatchFactory(team=team4, enemy_team=None)
        MatchFactory(team=team, enemy_team=team4)
        team5 = TeamFactory(name="Related team 2")
        MatchFactory(team=team, enemy_team=team5)
        MatchFactory(team=team3, enemy_team=team5)

        result = Team.objects.cleanup(ChannelTeam.objects.filter(team__in=[team, team3]))
        self.assertListEqual(["Delete me", "Delete me 2", "Related team", "Related team 2"], result)
        self.assertModelObjectsListEqual(
            [
                {"name": "Not me"},
            ],
            Team.objects.all(),
        )
        self.assertEqual(Match.objects.count(), 1)
        self.assertTrue(result)

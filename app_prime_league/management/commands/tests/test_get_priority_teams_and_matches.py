from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import make_aware

from app_prime_league.management.commands.updates_in_group_stage_and_playoffs import get_priority_teams_and_matches
from app_prime_league.models import Match, Team


class GetPriorityTeamsAndMatchesTest(TestCase):
    @patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.timezone.now")
    def test_update_all_teams(self, mock_now):
        now = make_aware(datetime(2024, 10, 14, 0, 0))
        # Mock the current time to be 0 AM on a Monday
        mock_now.return_value = now  # Monday

        registered_team = Team.objects.create(name="Registered Team", discord_channel_id=1)
        Team.objects.filter(id=registered_team.id).update(updated_at=now - timedelta(hours=1))
        Team.objects.create(name="Unregistered Team")
        enemy_team1 = Team.objects.create(name="Enemy Team")
        Team.objects.filter(id=enemy_team1.id).update(updated_at=now - timedelta(hours=2))
        enemy_team2 = Team.objects.create(name="Enemy Team 2")
        Team.objects.filter(id=enemy_team2.id).update(updated_at=now - timedelta(hours=3))
        Match.objects.create(
            team=registered_team,
            match_id=1,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=1),
            has_side_choice=True,
        )
        Match.objects.create(
            team=registered_team,
            match_id=2,
            enemy_team=enemy_team2,
            begin=now + timedelta(weeks=4),
            has_side_choice=True,
        )

        with patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.MAX_UPDATES", 3):
            teams, matches = get_priority_teams_and_matches()

        self.assertSetEqual(teams, {enemy_team2, enemy_team1, registered_team})
        self.assertSetEqual(matches, set())

    @patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.timezone.now")
    def test_update_all_matches(self, mock_now):
        # Mock the current time to be 4 AM on a Monday
        now = make_aware(datetime(2024, 10, 14, 4, 0))
        mock_now.return_value = now

        registered_team = Team.objects.create(name="Registered Team", discord_channel_id=1)
        Team.objects.create(name="Unregistered Team")
        enemy_team1 = Team.objects.create(name="Enemy Team")
        enemy_team2 = Team.objects.create(name="Enemy Team 2")
        match1 = Match.objects.create(
            team=registered_team,
            match_id=1,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=1),
            has_side_choice=True,
        )
        match2 = Match.objects.create(
            team=registered_team,
            match_id=2,
            enemy_team=enemy_team2,
            begin=now + timedelta(weeks=4),
            has_side_choice=True,
        )

        teams, matches = get_priority_teams_and_matches()

        self.assertSetEqual(teams, set())
        self.assertSetEqual(matches, {match1, match2})

    @patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.timezone.now")
    def test_update_priority_teams_and_matches(self, mock_now):
        # Mock the current time to be 5 AM on a Monday
        now = make_aware(datetime(2024, 10, 14, 5, 0))
        mock_now.return_value = now

        registered_team = Team.objects.create(name="Registered Team", discord_channel_id=1)
        Team.objects.create(name="Unregistered Team")
        enemy_team1 = Team.objects.create(name="Enemy Team")
        enemy_team2 = Team.objects.create(name="Enemy Team 2")
        match1 = Match.objects.create(
            team=registered_team,
            match_id=1,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=1),
            has_side_choice=True,
        )
        Match.objects.create(
            team=registered_team,
            match_id=2,
            enemy_team=enemy_team2,
            begin=now + timedelta(weeks=4),
            has_side_choice=True,
        )

        with patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.MAX_UPDATES", 3):
            teams, matches = get_priority_teams_and_matches()

        self.assertSetEqual(teams, {registered_team, enemy_team1})
        self.assertSetEqual(matches, {match1})

    @patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.timezone.now")
    def test_update_no_duplicates(self, mock_now):
        # Mock the current time to be 5 AM on a Monday
        now = make_aware(datetime(2024, 10, 14, 5, 0))
        mock_now.return_value = now

        registered_team = Team.objects.create(name="Registered Team", discord_channel_id=1)
        Team.objects.create(name="Unregistered Team")
        enemy_team1 = Team.objects.create(name="Enemy Team")
        Team.objects.create(name="Enemy Team 2")
        match1 = Match.objects.create(
            team=registered_team,
            match_id=1,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=1),
            has_side_choice=True,
        )
        Match.objects.filter(id=match1.id).update(updated_at=now - timedelta(hours=3))
        match2 = Match.objects.create(
            team=registered_team,
            match_id=2,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=2),
            has_side_choice=True,
        )
        Match.objects.filter(id=match2.id).update(updated_at=now - timedelta(hours=2))
        match3 = Match.objects.create(
            team=registered_team,
            match_id=3,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=3),
            has_side_choice=True,
        )
        Match.objects.filter(id=match3.id).update(updated_at=now - timedelta(hours=1))
        Match.objects.create(
            team=registered_team,
            match_id=4,
            enemy_team=enemy_team1,
            begin=now + timedelta(weeks=4),
            has_side_choice=True,
        )

        with patch("app_prime_league.management.commands.updates_in_group_stage_and_playoffs.MAX_UPDATES", 5):
            teams, matches = get_priority_teams_and_matches()

        self.assertSetEqual(teams, {registered_team, enemy_team1})
        self.assertSetEqual(matches, {match1, match2, match3})

from django.test import TestCase

from app_prime_league.models import Match, Team, Player
from modules.comparing.match_comparer import MatchComparer, TemporaryMatchData
from modules.tests.test_utils import string_to_datetime


class SuggestionsTest(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(id=1, name="Team 1", team_tag="T1")
        self.enemy_team = Team.objects.create(id=2, name="Team 2", team_tag="T2")

    def test_enemy_made_a_first_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=False,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=True),
                        "Enemy Team had new suggestion, but was not recognized")

    def test_enemy_has_existing_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=False,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_new_suggestion(of_enemy_team=True),
                         "Enemy Team has existing suggestion, but not new")

    def test_enemy_made_new_suggestion_after_own_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=False,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=True),
                        "Enemy Team had new suggestion, but was not recognized")

    def test_team_made_a_first_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=True,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=False),
                        "Team had new suggestion, but was not recognized")

    def test_team_has_existing_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=True,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_new_suggestion(of_enemy_team=False),
                         "Team has existing suggestion, but not new")

    def test_team_made_new_suggestion_after_enemy_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=True,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=False),
                        "Team had new suggestion, but was not recognized")


class CompareConfirmationTest(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(id=1, name="Team 1", team_tag="T1")
        self.enemy_team = Team.objects.create(id=2, name="Team 2", team_tag="T2")

    def test_new_accepted_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, match_begin_confirmed=True)
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_scheduling_confirmation(), "Enemy accepted suggestion, but was not recognized")

    def test_still_accepted_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, match_begin_confirmed=True)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, match_begin_confirmed=True)
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_scheduling_confirmation(), "Accepted Match Begin, but was recognized as new")

    def test_no_accepted_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, match_begin_confirmed=False)
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_scheduling_confirmation(), "No accepted Match Begin, but was recognized")


class CompareNewLineupTest(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(id=1, name="Team 1", team_tag="T1")
        self.enemy_team = Team.objects.create(id=2, name="Team 2", team_tag="T2")

    def test_no_lineup(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, )

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team)
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_lineup_confirmation(), "Enemy has no lineup, but was not recognized")

    def test_fresh_new_lineup(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, )

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, enemy_lineup=[
            (1, "Player 1", "Summonername 1", None),
            (2, "Player 2", "Summonername 2", None),
            (3, "Player 3", "Summonername 3", None),
            (4, "Player 4", "Summonername 4", None),
            (5, "Player 5", "Summonername 5", None),
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_lineup_confirmation(), "Enemy has fresh new lineup, but was not recognized")

    def test_existing_lineup(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, )
        players = Player.objects.create_or_update_players([
            (1, "Player 1", "Summonername 1", False),
            (5, "Player 5", "Summonername 5", False),
        ], self.enemy_team)
        match.enemy_lineup.add(*players)
        match.save()
        match.refresh_from_db()
        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, enemy_lineup=[
            (1, "Player 1", "Summonername 1", None),
            (5, "Player 5", "Summonername 5", None),
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_lineup_confirmation(), "Enemy has no new lineup, but was not recognized as new")

    def test_new_lineup(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, )
        players = Player.objects.create_or_update_players([
            (1, "Player 1", "Summonername 1", False),
            (5, "Player 5", "Summonername 5", False),
        ], self.enemy_team)
        match.enemy_lineup.add(*players)
        match.save()
        match.refresh_from_db()
        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, enemy_lineup=[
            (1, "Player 1", "Summonername 1", None),
            (2, "Player 2", "Summonername 2", None),
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_lineup_confirmation(), "Enemy has new lineup, but was not recognized")


def create_temporary_match_data(match_id=1, match_day=1, team=None, enemy_team=None, closed=False,
                                team_made_latest_suggestion=None, latest_suggestions=None, begin=None,
                                latest_confirmation_log=None, enemy_lineup=None, match_begin_confirmed=False):
    if latest_suggestions is None:
        latest_suggestions = []
    data = {
        "match_id": match_id,
        "match_day": match_day,
        "team": team if team else team,
        "enemy_team_id": enemy_team.id if enemy_team else enemy_team.id,
        "enemy_lineup": enemy_lineup,
        "closed": closed,
        "team_made_latest_suggestion": team_made_latest_suggestion,
        "latest_suggestions": latest_suggestions,
        "begin": begin,
        "latest_confirmation_log": latest_confirmation_log,
        "result": None,
        "match_begin_confirmed": match_begin_confirmed,
    }
    return TemporaryMatchData(**data)

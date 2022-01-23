import unittest

from django.test import TestCase

from app_prime_league.models import Match, Team
from modules.comparing.match_comparer import MatchComparer, TemporaryMatchData
from modules.comparing.tests.test_utils import string_to_datetime
from modules.parsing.logs import LogSchedulingConfirmation, LogSchedulingAutoConfirmation


class MatchComparerTest(TestCase):

    def setUp(self) -> None:
        self.team = Team.objects.create(id=1, name="Team 1", team_tag="T1")
        self.enemy_team = Team.objects.create(id=2, name="Team 2", team_tag="T2")

    def create_temporary_match_data(self, match_id=1, match_day=1, team=None, enemy_team=None, closed=False,
                                    team_made_latest_suggestion=None, latest_suggestions=[], match_begin=None,
                                    latest_confirmation_log=None):
        data = {
            "match_id": match_id,
            "match_day": match_day,
            "team": team if team else self.team,
            "enemy_team_id": enemy_team.id if enemy_team else self.enemy_team.id,
            "enemy_lineup": None,
            "closed": closed,
            "team_made_latest_suggestion": team_made_latest_suggestion,
            "latest_suggestions": latest_suggestions,
            "match_begin": match_begin,
            "latest_confirmation_log": latest_confirmation_log,
            "result": None
        }
        return TemporaryMatchData.create_from_dict(**data)


class SuggestionsTest(MatchComparerTest):

    def test_enemy_made_a_first_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team)

        md = self.create_temporary_match_data(team_made_latest_suggestion=False, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=True),
                        "Enemy Team had new suggestion, but was not recognized")

    def test_enemy_has_existing_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = self.create_temporary_match_data(team_made_latest_suggestion=False, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_new_suggestion(of_enemy_team=True),
                         "Enemy Team has existing suggestion, but not new")

    def test_enemy_made_new_suggestion_after_own_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = self.create_temporary_match_data(team_made_latest_suggestion=False, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=True),
                        "Enemy Team had new suggestion, but was not recognized")

    def test_team_made_a_first_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team)

        md = self.create_temporary_match_data(team_made_latest_suggestion=True, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=False),
                        "Team had new suggestion, but was not recognized")

    def test_team_has_existing_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = self.create_temporary_match_data(team_made_latest_suggestion=True, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertFalse(cp.compare_new_suggestion(of_enemy_team=False),
                         "Team has existing suggestion, but not new")

    def test_team_made_new_suggestion_after_enemy_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = self.create_temporary_match_data(team_made_latest_suggestion=True, latest_suggestions=[
            string_to_datetime("2022-01-01 17:00")
        ])
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_new_suggestion(of_enemy_team=False),
                        "Team had new suggestion, but was not recognized")


class CompareConfirmationTest(MatchComparerTest):
    def test_enemy_accepted_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=True)

        md = self.create_temporary_match_data(
            match_begin=string_to_datetime("2022-01-01 17:00"),
            latest_confirmation_log=LogSchedulingConfirmation(timestamp="1642948400", user_id=1,
                                                              details="Sun, 03 Oct 2021 15:00:00 +0200")
        )
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_scheduling_confirmation(), "Enemy accepted suggestion, but was not recognized")

    def test_team_accepted_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = self.create_temporary_match_data(
            match_begin=string_to_datetime("2022-01-01 17:00"),
            latest_confirmation_log=LogSchedulingConfirmation(timestamp="1642948400", user_id=1,
                                                              details="Sun, 03 Oct 2021 15:00:00 +0200")
        )
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_scheduling_confirmation(), "Team accepted suggestion, but was not recognized")

    def test_auto_confirmation(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team, team_made_latest_suggestion=False)

        md = self.create_temporary_match_data(
            match_begin=string_to_datetime("2022-01-01 17:00"),
            latest_confirmation_log=LogSchedulingAutoConfirmation(timestamp="1642948400", user_id=1,
                                                                  details="Sun, 03 Oct 2021 15:00:00 +0200")
        )
        cp = MatchComparer(match_old=match, match_new=md)
        self.assertTrue(cp.compare_scheduling_confirmation(), "Auto confirmation, but was not recognized")


if __name__ == '__main__':
    unittest.main()

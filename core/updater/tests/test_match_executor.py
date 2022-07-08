from django.test import TestCase

from app_prime_league.models import Team, Match
from bots.message_dispatcher import MessageCollector
from bots.messages import EnemyNewTimeSuggestionsNotificationMessage
from core.test_utils import create_temporary_match_data, string_to_datetime


class CollectorTest(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(id=1, name="Team 1", team_tag="T1")
        self.enemy_team = Team.objects.create(id=2, name="Team 2", team_tag="T2")

    def test_enemy_made_a_first_suggestion(self):
        match = Match.objects.create(match_id=1, match_day=1, match_type=Match.MATCH_TYPE_LEAGUE, team=self.team,
                                     enemy_team=self.enemy_team,
                                     has_side_choice=True)

        md = create_temporary_match_data(team=self.team, enemy_team=self.enemy_team, team_made_latest_suggestion=False,
                                         latest_suggestions=[
                                             string_to_datetime("2022-01-01 17:00")
                                         ])
        collector = MessageCollector(team=self.team)
        collector.dispatch(EnemyNewTimeSuggestionsNotificationMessage, match=match)


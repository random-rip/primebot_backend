from django.test import TestCase
from django.utils import translation

from app_prime_league.models import Team, Match, Player
from bots.messages import NewCommentsNotificationMessage
from core.test_utils import string_to_datetime
from utils.utils import format_datetime


class DiscordMessageTests(TestCase):

    def setUp(self):
        self.team_a = Team.objects.create(id=1, name="ABC", team_tag="abc", )
        self.team_b = Team.objects.create(id=2, name="XYZ", team_tag="xyz", )
        self.match = Match.objects.create(match_id=1, team=self.team_a, enemy_team=self.team_b, match_day=1,
                                          has_side_choice=True)
        line_up_players = [
            Player.objects.create(name="player 1", summoner_name="player1", team=self.team_b, ),
            Player.objects.create(name="player 2", summoner_name="player2", team=self.team_b),
            Player.objects.create(name="player 3", summoner_name="player3", team=self.team_b),
            Player.objects.create(name="player 4", summoner_name="player4", team=self.team_b),
            Player.objects.create(name="player 5", summoner_name="player5", team=self.team_b),
        ]
        Player.objects.create(name="player 6", summoner_name="player6", team=self.team_b),
        self.match.enemy_lineup.add(*line_up_players)

    def test_i18n(self):
        # todo test i18n
        self.team_a.language = "de"
        msg = NewCommentsNotificationMessage(match=self.match, team=self.team_a, new_comment_ids=[123456789])
        result = msg.generate_message()

        expected = ("Es gibt [einen neuen Kommentar](https://www.primeleague.gg/de/leagues/matches/1#comment:"
                    "123456789) für [Spieltag 1](https://www.primeleague.gg/de/leagues/"
                    "matches/1#comment:123456789) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2).")

        # print("Result:")
        # print(result)
        # print("Expected:")
        # print(expected)
        self.assertEqual(result, expected, )

    def test_datetime_format(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        with translation.override("de"):
            result = format_datetime(self.match.begin)
        self.assertEqual(
            "Donnerstag, 17. Februar 2022 15:00 Uhr",
            result,
        )
        self.assertEqual(
            format_datetime(self.match.begin),
            "Thursday, 17. February 2022 15:00 PM",
        )

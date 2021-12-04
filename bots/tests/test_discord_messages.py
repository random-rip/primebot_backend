from django.test import TestCase

from app_prime_league.models import Team, Game, Player
from bots.messages import WeeklyNotificationMessage, NewGameNotification


class DiscordMessageTests(TestCase):

    def setUp(self):
        self.team_a = Team.objects.create(id=1, name="ABC", team_tag="abc", )
        self.team_b = Team.objects.create(id=2, name="XYZ", team_tag="xyz", )
        self.game = Game.objects.create(game_id=1, team=self.team_a, enemy_team=self.team_b, game_day=1)
        Player.objects.create(name="player 1", summoner_name="player1", team=self.team_b)
        Player.objects.create(name="player 2", summoner_name="player2", team=self.team_b)
        Player.objects.create(name="player 3", summoner_name="player3", team=self.team_b)
        Player.objects.create(name="player 4", summoner_name="player4", team=self.team_b)
        Player.objects.create(name="player 5", summoner_name="player5", team=self.team_b)

    def test_weekly_notification(self):
        msg = WeeklyNotificationMessage(game=self.game, team=self.team_a)

        self.assertEqual(msg.msg_type, "weekly_notification", )
        self.assertEqual(msg._key, "weekly_op_link", )
        self.assertEqual(msg._attachable_key, "pin_weekly_op_link", )
        self.assertEqual(msg.mentionable, True, )
        self.assertEqual(msg._attachable, True, )

        assertion_msg = ("Der nächste Spieltag:\n🔜[Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1) gegen"
                         " [xyz](https://www.primeleague.gg/de/leagues/teams/2):\nHier ist der [OP.GG Link]"
                         "(https://euw.op.gg/multi/?query=player1,player2,player3,player4,player5) des Teams.")
        self.assertEqual(msg.message, assertion_msg, )

    def test_new_game_notification(self):
        msg = NewGameNotification(game=self.game, team=self.team_a)

        self.assertEqual(msg.msg_type, "new_game_notification", )
        self.assertEqual(msg._key, "new_game_notification", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = ("Euer nächstes Spiel in der Kalibrierungsphase:\n"
                         "🔜[Spiel 1](https://www.primeleague.gg/de/leagues/matches/1) gegen [xyz](https://www.primeleag"
                         "ue.gg/de/leagues/teams/2):\nHier ist der [OP.GG Link](https://euw"
                         ".op.gg/multi/?query=player1,player2,player3,player4,player5) des Teams.")
        self.assertEqual(msg.message, assertion_msg, )

from django.test import TestCase

from app_prime_league.models import Team, Game, Player
from communication_interfaces.messages import WeeklyNotificationMessage


class DiscordMessageTests(TestCase):

    def setUp(self) -> None:
        self.team_a = Team.objects.create(name="ABC", team_tag="abc", )
        self.team_b = Team.objects.create(name="XYZ", team_tag="xyz", )
        self.game = Game.objects.create(game_id=1, team=self.team_a, enemy_team=self.team_b)
        Player.objects.create(name="player 1", summoner_name="player 1", team=self.team_b)
        Player.objects.create(name="player 2", summoner_name="player 2", team=self.team_b)
        Player.objects.create(name="player 3", summoner_name="player 3", team=self.team_b)
        Player.objects.create(name="player 4", summoner_name="player 4", team=self.team_b)
        Player.objects.create(name="player 5", summoner_name="player 5", team=self.team_b)

    def weekly_notification(self):
        msg = WeeklyNotificationMessage(game=self.game, team=self.team_a)

        self.assertEqual(

        )
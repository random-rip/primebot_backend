from django.test import TestCase

from app_prime_league.models import Team, Match, Player, Suggestion
from bots.messages import WeeklyNotificationMessage, NewMatchNotification, NewLineupNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, EnemyNewTimeSuggestionsNotificationMessage, \
    ScheduleConfirmationNotification
from modules.parsing.logs import LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime
from modules.tests.test_utils import string_to_datetime


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

    def test_weekly_notification(self):
        msg = WeeklyNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg._key, "WEEKLY_MATCH_DAY", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = ("Der nächste Spieltag:\n🔜[Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1) gegen"
                         " [xyz](https://www.primeleague.gg/de/leagues/teams/2):\n"
                         "Hier ist der [op.gg Link](https://euw.op.gg/multisearch/euw?summoners=player1,player2,"
                         "player3,player4,player5,player6) des Teams.")

        self.assertEqual(msg.message, assertion_msg, )

    def test_new_lineup(self):
        msg = NewLineupNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg._key, "LINEUP_NOTIFICATION", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = (
            "[xyz](https://www.primeleague.gg/de/leagues/teams/2) ([Spieltag 1](https://www.primeleague.gg/de/"
            "leagues/matches/1)) hat ein neues [Lineup](https://euw.op.gg/multisearch/euw?summoners=player1,player"
            "2,player3,player4,player5) aufgestellt. 📈🆙"
        )

        self.assertEqual(msg.message, assertion_msg, )

    def test_own_time_suggestions(self):
        msg = OwnNewTimeSuggestionsNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg._key, "TEAM_SCHEDULING_SUGGESTION", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = (
            "Neuer Terminvorschlag von euch für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1). ✅"
        )

        self.assertEqual(msg.message, assertion_msg, )

    def test_enemy_time_suggestions(self):
        Suggestion.objects.create(begin=string_to_datetime("2022-01-01 17:30"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 15:00"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 17:00"), match=self.match)

        msg = EnemyNewTimeSuggestionsNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg._key, "ENEMY_SCHEDULING_SUGGESTION", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = (
            "Neue Terminvorschläge von [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "1️⃣Samstag, 1. Jan. 2022 17:30Uhr\n"
            "2️⃣Sonntag, 2. Jan. 2022 15:00Uhr\n"
            "3️⃣Sonntag, 2. Jan. 2022 17:00Uhr"
        )
        self.assertEqual(msg.message, assertion_msg, )

    def test_schedule_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        self.assertEqual(msg._key, "SCHEDULING_CONFIRMATION", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = (
            "Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Feb. 2022 15:00Uhr"
        )
        self.assertEqual(msg.message, assertion_msg, )

    def test_schedule_auto_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingAutoConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        assertion_msg = (
            "Automatische Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1]"
            "(https://www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Feb. 2022 15:00Uhr"
        )
        self.assertEqual(msg.message, assertion_msg, )

    def test_admin_changed_time(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogChangeTime(1645120288, "", "Manually adjusted time to 2022-02-17 15:00 +01:00")
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        assertion_msg = (
            "Ein Administrator hat eine neue Zeit für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1) "
            "gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) festgelegt:\n"
            "⚔Donnerstag, 17. Feb. 2022 15:00Uhr"
        )
        self.assertEqual(msg.message, assertion_msg, )

    def test_new_match_notification(self):
        msg = NewMatchNotification(match=self.match, team=self.team_a)

        self.assertEqual(msg._key, "NEW_MATCH_NOTIFICATION", )
        self.assertEqual(msg.mentionable, True, )

        assertion_msg = ("Euer nächstes Spiel in der Kalibrierungsphase:\n"
                         "🔜[Spiel 1](https://www.primeleague.gg/de/leagues/matches/1) gegen [xyz](https://www.primeleag"
                         "ue.gg/de/leagues/teams/2):\nHier ist der [op.gg Link](https://euw.op.gg/multisearch/euw?"
                         "summoners=player1,player2,player3,player4,player5,player6) des Teams.")

        self.assertEqual(msg.message, assertion_msg, )

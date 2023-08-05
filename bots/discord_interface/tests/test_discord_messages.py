from datetime import datetime
from unittest import mock

import pytz
from django.conf import settings
from django.test import TestCase

from app_prime_league.models import Team, Match, Player, Suggestion
from bots.messages import NewLineupNotificationMessage, WeeklyNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, EnemyNewTimeSuggestionsNotificationMessage, \
    ScheduleConfirmationNotification, NewMatchNotification, NewCommentsNotificationMessage
from core.parsing.logs import LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime
from core.test_utils import string_to_datetime


class DiscordMessageTests(TestCase):

    def setUp(self):
        self.team_a = Team.objects.create(id=1, name="ABC", team_tag="abc", )
        self.team_b = Team.objects.create(id=2, name="XYZ", team_tag="xyz", )
        self.match = Match.objects.create(match_id=1, team=self.team_a, enemy_team=self.team_b, match_day=1,
                                          has_side_choice=True,
                                          begin=datetime(2023, 3, 15, 12, tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                          closed=False)
        line_up_players = [
            Player.objects.create(name="player 1", summoner_name="player1", team=self.team_b, ),
            Player.objects.create(name="player 2", summoner_name="player2", team=self.team_b),
            Player.objects.create(name="player 3", summoner_name="player3", team=self.team_b),
            Player.objects.create(name="player 4", summoner_name="player4", team=self.team_b),
            Player.objects.create(name="player 5", summoner_name="player5", team=self.team_b),
        ]
        Player.objects.create(name="player 6", summoner_name="player6", team=self.team_b),
        self.match.enemy_lineup.add(*line_up_players)

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=pytz.timezone(settings.TIME_ZONE)))
        msg = WeeklyNotificationMessage(team=self.team_a)

        self.assertEqual(msg.settings_key, "WEEKLY_MATCH_DAY", )
        self.assertEqual(msg.mentionable, True, )

        expected = ("**Folgende Matches finden diese Woche statt:**\n\n[Spieltag 1]"
                    "(https://www.primeleague.gg/de/leagues/matches/1) ⚔ "
                    "XYZ ➡ [op.gg](https://euw.op.gg/multisearch/euw?summoners=player1,player2,"
                    "player3,player4,player5,player6)\n")

        self.assertEqual(expected, msg.generate_message(), )

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification_no_new_matches(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=pytz.timezone(settings.TIME_ZONE)))
        msg = WeeklyNotificationMessage(team=self.team_a)

        self.assertEqual(msg.settings_key, "WEEKLY_MATCH_DAY", )
        self.assertEqual(msg.mentionable, True, )

        expected = ("**Folgende Matches finden diese Woche statt:**\n\n[Spieltag 1]"
                    "(https://www.primeleague.gg/de/leagues/matches/1) ⚔ "
                    "XYZ ➡ [op.gg](https://euw.op.gg/multisearch/euw?summoners=player1,player2,"
                    "player3,player4,player5,player6)\n")

        self.assertEqual(expected, msg.generate_message(), )

    def test_new_lineup(self):
        msg = NewLineupNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg.settings_key, "LINEUP_NOTIFICATION", )
        self.assertEqual(msg.mentionable, True, )

        expected = (
            "[xyz](https://www.primeleague.gg/de/leagues/teams/2) ([Spieltag 1](https://www.primeleague.gg/de/"
            "leagues/matches/1)) hat ein neues [Lineup](https://euw.op.gg/multisearch/euw?summoners=player1,player"
            "2,player3,player4,player5) aufgestellt."
        )

        self.assertEqual(expected, msg.generate_message(), )

    def test_own_time_suggestions(self):
        Suggestion.objects.create(begin=string_to_datetime("2022-01-01 17:30"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 15:00"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 17:00"), match=self.match)

        msg = OwnNewTimeSuggestionsNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual(msg.settings_key, "TEAM_SCHEDULING_SUGGESTION", )
        self.assertEqual(msg.mentionable, True, )

        expected = (
            "Neue Terminvorschläge von euch für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1):\n"
            "1️⃣Samstag, 1. Januar 2022 17:30 Uhr\n"
            "2️⃣Sonntag, 2. Januar 2022 15:00 Uhr\n"
            "3️⃣Sonntag, 2. Januar 2022 17:00 Uhr"
        )

        self.assertEqual(expected, msg.generate_message(), )

    def test_enemy_time_suggestions(self):
        Suggestion.objects.create(begin=string_to_datetime("2022-01-01 17:30"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 15:00"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 17:00"), match=self.match)

        msg = EnemyNewTimeSuggestionsNotificationMessage(match=self.match, team=self.team_a)

        self.assertEqual("ENEMY_SCHEDULING_SUGGESTION", msg.settings_key, )
        self.assertTrue(msg.mentionable, )
        self.assertEqual("📆 Neuer Terminvorschlag eines Gegners", msg.generate_title(), )

        expected = (
            "Neue Terminvorschläge von [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "1️⃣Samstag, 1. Januar 2022 17:30 Uhr\n"
            "2️⃣Sonntag, 2. Januar 2022 15:00 Uhr\n"
            "3️⃣Sonntag, 2. Januar 2022 17:00 Uhr"
        )
        self.assertEqual(expected, msg.generate_message())

    def test_schedule_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        self.assertEqual(msg.settings_key, "SCHEDULING_CONFIRMATION", )
        self.assertEqual(msg.mentionable, True, )

        expected = (
            "Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(expected, msg.generate_message(), )

    def test_schedule_auto_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingAutoConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        expected = (
            "Automatische Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) für [Spieltag 1]"
            "(https://www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(expected, msg.generate_message(), )

    def test_admin_changed_time(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogChangeTime(1645120288, "", "Manually adjusted time to 2022-02-17 15:00 +01:00")
        msg = ScheduleConfirmationNotification(match=self.match, team=self.team_a, latest_confirmation_log=log)

        expected = (
            "Ein Administrator hat eine neue Zeit für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1) "
            "gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2) festgelegt:\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(expected, msg.generate_message(), )

    def test_new_match_notification(self):
        self.match.match_type = Match.MATCH_TYPE_GROUP
        msg = NewMatchNotification(match=self.match, team=self.team_a)

        self.assertEqual(msg.settings_key, "NEW_MATCH_NOTIFICATION", )
        self.assertEqual(msg.mentionable, True, )
        expected = ("Euer nächstes Match in der Kalibrierungsphase:\n"
                    "[Match 1](https://www.primeleague.gg/de/leagues/matches/1) gegen [xyz](https://www.primeleag"
                    "ue.gg/de/leagues/teams/2):\nHier ist der [op.gg Link](https://euw.op.gg/multisearch/euw?"
                    "summoners=player1,player2,player3,player4,player5,player6) des Teams.")

        self.assertEqual(expected, msg.generate_message(), )

    def test_new_comments_notification(self):
        msg = NewCommentsNotificationMessage(match=self.match, team=self.team_a, new_comment_ids=[123456789])

        self.assertEqual(msg.settings_key, "NEW_COMMENTS_OF_UNKNOWN_USERS", )
        self.assertEqual(msg.mentionable, True, )

        expected = ("Es gibt [einen neuen Kommentar](https://www.primeleague.gg/de/leagues/matches/1#comment:"
                    "123456789) für [Spieltag 1](https://www.primeleague.gg/de/leagues/"
                    "matches/1#comment:123456789) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2).")

        self.assertEqual(expected, msg.generate_message(), )

        msg = NewCommentsNotificationMessage(match=self.match, team=self.team_a, new_comment_ids=[123, 456, 789])
        expected = ("Es gibt [neue Kommentare](https://www.primeleague.gg/de/leagues/matches/1#comment:123) für "
                    "[Spieltag 1](https://www.primeleague.gg/de/leagues/matches"
                    "/1#comment:123) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/2).")

        self.assertEqual(expected, msg.generate_message(), )


class WeeklyNotificationTests(TestCase):

    def setUp(self):
        self.team_a = Team.objects.create(id=1, name="ABC", team_tag="abc", )
        self.team_b = Team.objects.create(id=2, name="XYZ", team_tag="xyz", )

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=pytz.timezone(settings.TIME_ZONE)))
        self.match = Match.objects.create(match_id=1, team=self.team_a, enemy_team=self.team_b, match_day=1,
                                          has_side_choice=True,
                                          begin=datetime(2023, 3, 15, 12, tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                          closed=False)
        msg = WeeklyNotificationMessage(team=self.team_a)
        line_up_players = [
            Player.objects.create(name="player 1", summoner_name="player1", team=self.team_b, ),
            Player.objects.create(name="player 2", summoner_name="player2", team=self.team_b),
            Player.objects.create(name="player 3", summoner_name="player3", team=self.team_b),
            Player.objects.create(name="player 4", summoner_name="player4", team=self.team_b),
            Player.objects.create(name="player 5", summoner_name="player5", team=self.team_b),
        ]
        Player.objects.create(name="player 6", summoner_name="player6", team=self.team_b),
        self.match.enemy_lineup.add(*line_up_players)
        self.assertEqual(msg.settings_key, "WEEKLY_MATCH_DAY", )
        self.assertEqual(msg.mentionable, True, )

        expected = ("**Folgende Matches finden diese Woche statt:**\n\n[Spieltag 1]"
                    "(https://www.primeleague.gg/de/leagues/matches/1) ⚔ "
                    "XYZ ➡ [op.gg](https://euw.op.gg/multisearch/euw?summoners=player1,player2,"
                    "player3,player4,player5,player6)\n")

        self.assertEqual(expected, msg.generate_message(), )

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification_no_new_matches(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=pytz.timezone(settings.TIME_ZONE)))
        self.match = Match.objects.create(match_id=1, team=self.team_a, enemy_team=self.team_b, match_day=1,
                                          has_side_choice=True,
                                          begin=datetime(2023, 3, 8, 12, tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                          closed=False)
        self.match = Match.objects.create(match_id=2, team=self.team_a, enemy_team=self.team_b, match_day=1,
                                          has_side_choice=True,
                                          begin=datetime(2023, 3, 25, 12, tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                          closed=False)
        msg = WeeklyNotificationMessage(team=self.team_a)

        self.assertEqual(msg.settings_key, "WEEKLY_MATCH_DAY", )
        self.assertEqual(msg.mentionable, True, )

        expected = "Ihr habt keine Matches diese Woche."

        self.assertEqual(expected, msg.generate_message(), )

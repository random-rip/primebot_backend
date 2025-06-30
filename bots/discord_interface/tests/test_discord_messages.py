from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django.conf import settings
from django.test import TestCase

from app_prime_league.factories import ChannelFactory, MatchFactory, PlayerFactory, TeamFactory
from app_prime_league.models import ChannelTeam, Match, Suggestion
from app_prime_league.models.channel import Platforms
from bots.messages import (
    EnemyNewTimeSuggestionsNotificationMessage,
    NewCommentsNotificationMessage,
    NewLineupNotificationMessage,
    OwnNewTimeSuggestionsNotificationMessage,
    ScheduleConfirmationNotification,
    WeeklyNotificationMessage,
)
from core.parsing.logs import LogChangeTime, LogSchedulingAutoConfirmation, LogSchedulingConfirmation
from core.test_utils import string_to_datetime


class SpecialCharacterTests(TestCase):
    def setUp(self):
        self.team_a = TeamFactory(name="ÄÖÜ", team_tag="äöü", channels=ChannelFactory(platform=Platforms.DISCORD))
        self.team_b = TeamFactory(
            name="ß", team_tag="ß", players=PlayerFactory(name="Förster", summoner_name="Förster")
        )
        self.match = MatchFactory(
            match_id=1,
            team=self.team_a,
            enemy_team=self.team_b,
            match_day=1,
            match_type=Match.MatchType.LEAGUE,
            closed=False,
            begin=datetime(2023, 3, 15, 12, tzinfo=ZoneInfo(settings.TIME_ZONE)),
            enemy_lineup=[
                PlayerFactory(name="Mörlin", summoner_name="Mörlin", team=self.team_b),
                PlayerFactory(name="ßßßßßß", summoner_name="ßßßßßß", team=self.team_b),
            ],
        )

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=ZoneInfo(settings.TIME_ZONE)))
        msg = WeeklyNotificationMessage(channel_team=ChannelTeam.objects.first())

        self.assertEqual(
            msg.settings_key,
            "WEEKLY_MATCH_DAY",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            "**Folgende Matches finden diese Woche statt:**\n\n[Spieltag 1]"
            "(https://www.primeleague.gg/de/leagues/matches/1) ⚔ "
            "ß ➡ [op.gg](https://www.op.gg/multisearch/euw?summoners=F%C3%B6rster,M%C3%B6rlin,"
            "%C3%9F%C3%9F%C3%9F%C3%9F%C3%9F%C3%9F)\n"
        )
        result = msg.generate_message()
        self.assertEqual(expected, result)


class DiscordMessageTests(TestCase):
    def setUp(self):
        self.team_a = TeamFactory(name="ABC", team_tag="abc", channels=ChannelFactory(platform=Platforms.DISCORD))
        self.team_b = TeamFactory(
            name="XYZ", team_tag="xyz", players=PlayerFactory(name="player 6", summoner_name="player6")
        )
        self.match = MatchFactory(
            match_id=1,
            match_type=Match.MatchType.LEAGUE,
            team=self.team_a,
            enemy_team=self.team_b,
            match_day=1,
            has_side_choice=True,
            begin=datetime(2023, 3, 15, 12, tzinfo=ZoneInfo(settings.TIME_ZONE)),
            closed=False,
            enemy_lineup=[
                PlayerFactory(name="player 1", summoner_name="player1", team=self.team_b),
                PlayerFactory(name="player 2", summoner_name="player2", team=self.team_b),
                PlayerFactory(name="player 3", summoner_name="player3", team=self.team_b),
                PlayerFactory(name="player 4", summoner_name="player4", team=self.team_b),
                PlayerFactory(name="player 5", summoner_name="player5", team=self.team_b),
            ],
        )

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=ZoneInfo(settings.TIME_ZONE)))
        msg = WeeklyNotificationMessage(channel_team=ChannelTeam.objects.first())

        self.assertEqual(
            msg.settings_key,
            "WEEKLY_MATCH_DAY",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            "**Folgende Matches finden diese Woche statt:**\n\n[Spieltag 1]"
            "(https://www.primeleague.gg/de/leagues/matches/1) ⚔ "
            "XYZ ➡ [op.gg](https://www.op.gg/multisearch/euw?summoners=player1,player2,"
            "player3,player4,player5,player6)\n"
        )

        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_new_lineup(self):
        msg = NewLineupNotificationMessage(channel_team=ChannelTeam.objects.first(), match=self.match)

        self.assertEqual(
            msg.settings_key,
            "LINEUP_NOTIFICATION",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            f"[xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id}) ([Spieltag 1](https://www.primeleague.gg/de/"
            "leagues/matches/1)) hat ein neues [Lineup](https://www.op.gg/multisearch/euw?summoners=player1,player"
            "2,player3,player4,player5) aufgestellt."
        )

        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_own_time_suggestions(self):
        Suggestion.objects.create(begin=string_to_datetime("2022-01-01 17:30"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 15:00"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 17:00"), match=self.match)

        msg = OwnNewTimeSuggestionsNotificationMessage(channel_team=ChannelTeam.objects.first(), match=self.match)

        self.assertEqual(
            msg.settings_key,
            "TEAM_SCHEDULING_SUGGESTION",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            "Neue Terminvorschläge von euch für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1):\n"
            "1️⃣Samstag, 1. Januar 2022 17:30 Uhr\n"
            "2️⃣Sonntag, 2. Januar 2022 15:00 Uhr\n"
            "3️⃣Sonntag, 2. Januar 2022 17:00 Uhr"
        )

        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_enemy_time_suggestions(self):
        Suggestion.objects.create(begin=string_to_datetime("2022-01-01 17:30"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 15:00"), match=self.match)
        Suggestion.objects.create(begin=string_to_datetime("2022-01-02 17:00"), match=self.match)

        msg = EnemyNewTimeSuggestionsNotificationMessage(channel_team=ChannelTeam.objects.first(), match=self.match)

        self.assertEqual(
            "ENEMY_SCHEDULING_SUGGESTION",
            msg.settings_key,
        )
        self.assertTrue(
            msg.mentionable,
        )
        self.assertEqual(
            "📆 Neuer Terminvorschlag eines Gegners",
            msg.generate_title(),
        )

        expected = (
            f"Neue Terminvorschläge von [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id}) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "1️⃣Samstag, 1. Januar 2022 17:30 Uhr\n"
            "2️⃣Sonntag, 2. Januar 2022 15:00 Uhr\n"
            "3️⃣Sonntag, 2. Januar 2022 17:00 Uhr"
        )
        self.assertEqual(expected, msg.generate_message())

    def test_schedule_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(
            channel_team=ChannelTeam.objects.first(), match=self.match, latest_confirmation_log=log
        )

        self.assertEqual(
            msg.settings_key,
            "SCHEDULING_CONFIRMATION",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            f"Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id}) für [Spieltag 1](https://"
            "www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_schedule_auto_confirmation(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogSchedulingAutoConfirmation(1645120288, "", 1645120288)
        msg = ScheduleConfirmationNotification(
            channel_team=ChannelTeam.objects.first(), match=self.match, latest_confirmation_log=log
        )

        expected = (
            f"Automatische Spielbestätigung gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id}) für [Spieltag 1]"
            "(https://www.primeleague.gg/de/leagues/matches/1):\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_admin_changed_time(self):
        self.match.begin = string_to_datetime("2022-02-17 15:00")
        log = LogChangeTime(1645120288, "", "Manually adjusted time to 2022-02-17 15:00 +01:00")
        msg = ScheduleConfirmationNotification(
            channel_team=ChannelTeam.objects.first(), match=self.match, latest_confirmation_log=log
        )

        expected = (
            "Ein Administrator hat eine neue Zeit für [Spieltag 1](https://www.primeleague.gg/de/leagues/matches/1) "
            f"gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id}) festgelegt:\n"
            "⚔Donnerstag, 17. Februar 2022 15:00 Uhr"
        )
        self.assertEqual(
            expected,
            msg.generate_message(),
        )

    def test_new_comments_notification(self):
        msg = NewCommentsNotificationMessage(
            channel_team=ChannelTeam.objects.first(), match=self.match, new_comment_ids=[123456789]
        )

        self.assertEqual(
            msg.settings_key,
            "NEW_COMMENTS_OF_UNKNOWN_USERS",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = (
            "Es gibt [einen neuen Kommentar](https://www.primeleague.gg/de/leagues/matches/1#comment:"
            "123456789) für [Spieltag 1](https://www.primeleague.gg/de/leagues/"
            f"matches/1) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id})."
        )

        self.assertEqual(
            expected,
            msg.generate_message(),
        )

        msg = NewCommentsNotificationMessage(
            channel_team=ChannelTeam.objects.first(), match=self.match, new_comment_ids=[123, 456, 789]
        )
        expected = (
            "Es gibt [neue Kommentare](https://www.primeleague.gg/de/leagues/matches/1#comment:123) für "
            "[Spieltag 1](https://www.primeleague.gg/de/leagues/matches"
            f"/1) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id})."
        )

        self.assertEqual(
            expected,
            msg.generate_message(),
        )


class WeeklyNotificationTests(TestCase):
    def setUp(self):
        self.team_a = TeamFactory(name="ABC", team_tag="abc", channels=ChannelFactory(platform=Platforms.DISCORD))
        self.team_b = TeamFactory(name="XYZ", team_tag="xyz")

    @mock.patch("bots.messages.weekly_notification.timezone")
    def test_weekly_notification_no_new_matches(self, timezone_mock):
        timezone_mock.now = mock.Mock(return_value=datetime(2023, 3, 13, 9, tzinfo=ZoneInfo(settings.TIME_ZONE)))
        self.match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
            match_day=1,
            match_type=Match.MatchType.LEAGUE,
            begin=datetime(2023, 3, 8, 12, tzinfo=ZoneInfo(settings.TIME_ZONE)),
            closed=False,
        )
        self.match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
            match_day=1,
            match_type=Match.MatchType.LEAGUE,
            begin=datetime(2023, 3, 25, 12, tzinfo=ZoneInfo(settings.TIME_ZONE)),
            closed=False,
        )
        msg = WeeklyNotificationMessage(channel_team=ChannelTeam.objects.first())

        self.assertEqual(
            msg.settings_key,
            "WEEKLY_MATCH_DAY",
        )
        self.assertEqual(
            msg.mentionable,
            True,
        )

        expected = "Ihr habt keine Matches diese Woche."

        self.assertEqual(
            expected,
            msg.generate_message(),
        )

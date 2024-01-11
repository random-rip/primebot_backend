import pytz
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils.datetime_safe import datetime
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from telegram import Chat

from app_prime_league.models import Team
from bots.telegram_interface.tests.commands.utils import MatchBuilder, TeamBuilder, TestBot, test_call_match


@override_settings(CURRENT_SPLIT_START=datetime(2022, 1, 1).astimezone(pytz.timezone(settings.TIME_ZONE)))
class TelegramMatchTestCase(TestCase):
    databases = ["default"]
    TELEGRAM_ID = 1

    def setUp(self) -> None:
        super().setUp()
        self.telegram_chat = Chat(self.TELEGRAM_ID, Chat.CHANNEL)
        self.bot = TestBot()

    def test_required_match_day_arg_is_missing(self):
        test_call_match("/match", self.telegram_chat, self.bot)

        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_match_day_arg_has_invalid_format(self):
        test_call_match("/zwei", self.telegram_chat, self.bot)

        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_match_day_arg_has_invalid_spacing(self):
        test_call_match("/match 2 2", self.telegram_chat, self.bot)

        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_no_registered_team_in_telegram_chat(self):
        test_call_match("/match 3", self.telegram_chat, self.bot)

        self.assertEqual("In der Telegram-Gruppe wurde noch kein Team registriert (/start).", self.bot.response_text)

    def test_at_match_day_are_no_matches(self):
        TeamBuilder("Team 1").set_telegram_id(self.TELEGRAM_ID).build()

        test_call_match("/match 3", self.telegram_chat, self.bot)

        self.assertEqual(_("Sadly there is no match on the given match day."), self.bot.response_text)

    def test_existing_match_day_without_lineups(self):
        team_1 = (
            TeamBuilder("Team 1")
            .add_players_by_names("player_1")
            .set_telegram_id(self.TELEGRAM_ID)
            .set_language(Team.Languages.ENGLISH)
            .build()
        )

        team_2 = TeamBuilder("Team 2").add_players_by_names("player 2").build()

        MatchBuilder(1, team_1, team_2).set_match_day(2).begin_at(make_aware(datetime(2022, 2, 2))).build()

        test_call_match("/match 2", self.telegram_chat, self.bot)

        expected = (
            "*⚔ Gameday 2*\n"
            "[against Team 2](https://www.primeleague.gg/de/leagues/matches/1)\n\n"
            "*Date*\n"
            "> 📆 No dates proposed. Alternative date: Wednesday, 2. February 2022 0:00 AM\n\n"
            "*Opposing team*\n"
            "> 🔍 [op.gg](https://euw.op.gg/multisearch/euw?summoners=)\n\n"
            "*Your lineup*\n"
            "⚠ No lineup has been submitted yet.\n\n"
            "*Lineup of opponent*\n"
            "No lineup has been submitted yet.\n\n"
            "*Other information*\n"
            "> You have a choice of sides in the *second* game.\n"
            "> The rulebook is available [here.](https://www.primeleague.gg/statics/rules_general)\n\n"
        )

        self.assertEqual(expected, self.bot.response_text)

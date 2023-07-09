from django.test import TestCase
from django.utils.datetime_safe import datetime
from django.utils.timezone import make_aware
from telegram import Chat

from app_prime_league.models import Match
from bots.telegram_interface.tests.commands.utils import test_call_match, TestBot, create_team_with_player_names


class TelegramMatchTestCase(TestCase):
    databases = ["default"]
    TELEGRAM_ID = 1

    def setUp(self) -> None:
        super().setUp()

        self.telegram_chat = Chat(self.TELEGRAM_ID, Chat.CHANNEL)
        self.bot = TestBot()

    def test_required_match_day_arg_is_missing(self):
        test_call_match("/match", self.telegram_chat, self.bot)

        self.assertEqual("Invalider Spieltag. Versuche es mit `/match 1`.", self.bot.response_text)

    def test_match_day_arg_has_invalid_format(self):
        test_call_match("/zwei", self.telegram_chat, self.bot)

        self.assertEqual("Invalider Spieltag. Versuche es mit `/match 1`.", self.bot.response_text)

    def test_match_day_arg_has_invalid_spacing(self):
        test_call_match("/match 2 2", self.telegram_chat, self.bot)

        self.assertEqual("Invalider Spieltag. Versuche es mit `/match 1`.", self.bot.response_text)

    def test_no_registered_team_in_telegram_chat(self):
        test_call_match("/match 3", self.telegram_chat, self.bot)

        self.assertEqual("In der Telegram-Gruppe wurde noch kein Team registriert (/start).", self.bot.response_text)

    def test_at_match_day_are_no_matches(self):
        create_team_with_player_names("Team 1", [], telegram_id=self.TELEGRAM_ID)

        test_call_match("/match 3", self.telegram_chat, self.bot)

        self.assertEqual("Leider existieren an dem von dir selektierten Tag keine Spiele.", self.bot.response_text)

    def test_existing_match_day_without_lineups(self):
        team_1 = create_team_with_player_names("Team 1", ["player_1"], telegram_id=self.TELEGRAM_ID)
        team_2 = create_team_with_player_names("Team 2", ["player_2", "player_3"])

        Match.objects.create(
            match_id=1, team=team_1, enemy_team=team_2, match_day=2, has_side_choice=False,
            match_type=Match.MATCH_TYPE_LEAGUE, begin=make_aware(datetime(2022, 2, 2))
        )

        test_call_match("/match 2", self.telegram_chat, self.bot)

        expected = (
            "*Disclaimer*\n"
            "This command is in beta! We still collect feedback for this.\n"
            "What other information would you like to see?\n"
            "[Write us on Discord](https://discord.gg/7NYgT2uFPm)\n"
            "*⚔ Gameday 2*\n"
            "[against Team 2](https://www.primeleague.gg/de/leagues/matches/1)\n\n"

            "*Date*\n"
            "> 📆 No dates proposed. Alternative date: Mittwoch, 2. Februar 2022 0:00 Uhr\n\n"

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

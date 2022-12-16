from django.test import TestCase
from telegram import Chat, Message, Update

from app_prime_league.models import Match, Team, Player
from bots.telegram_interface.commands.single_commands import call_match


class DummyChat(Chat):
    type = Chat.CHANNEL


class DummyBot:
    response_text: str = ''

    def send_message(self, chat_id, *args, **kwargs):
        self.response_text = args[0] if args else kwargs.get("text", "")

        return None


class TelegramMatchTestCase(TestCase):
    databases = ["default"]

    def setUp(self) -> None:
        super().setUp()

        self.chat = Chat(1, Chat.CHANNEL)
        self.bot = DummyBot()

        self.team = Team.objects.create(name="Team", telegram_id=1)
        Player.objects.create(name="player_1", team=self.team)
        Player.objects.create(name="player_2", team=self.team)
        Player.objects.create(name="player_3", team=self.team)

        self.enemy_team = Team.objects.create(name="Enemy Team")
        Player.objects.create(name="enemy_1", team=self.enemy_team)
        Player.objects.create(name="enemy_2", team=self.enemy_team)

        self.match = Match.objects.create(
            match_id=1,
            team=self.team,
            enemy_team=self.enemy_team,
            match_day=2,
            has_side_choice=False,
        )

    def update_factory(self, message: Message) -> Update:
        return Update(1, message)

    def message_factory(self, text: str):
        return Message(1, 1, None, self.chat, text=text, bot=self.bot)

    def simulate_call_match(self, text: str) -> str:
        message = self.message_factory(text)
        update = self.update_factory(message)

        call_match(update, None)

    def test_missing_match_day(self):
        self.simulate_call_match("/match")
        response_text = self.bot.response_text

        expected = "Invalider Spieltag. Versuche es mit `/match 1`."

        self.assertEqual(expected, response_text)

    def test_invalid_match_day_format(self):
        self.simulate_call_match("/match zwei")
        response_text = self.bot.response_text

        expected = "Invalider Spieltag. Versuche es mit `/match 1`."

        self.assertEqual(expected, response_text)

    def test_invalid_match_day_format_spacing(self):
        self.simulate_call_match("/match 2 2")
        response_text = self.bot.response_text

        expected = "Invalider Spieltag. Versuche es mit `/match 1`."

        self.assertEqual(expected, response_text)

    def test_match_day_has_no_matches(self):
        self.simulate_call_match("/match 3")
        response_text = self.bot.response_text

        expected = "Leider existieren an dem von dir selektierten Tag keine Spiele."

        self.assertEqual(expected, response_text)

    def test_existing_match_day_without_lineups(self):
        self.simulate_call_match("/match 2")
        response_text = self.bot.response_text

        expected = (
            "*Disclaimer*\n"
            "Dieser Befehl befindet sich noch in der Beta! Wir sammeln dazu noch Feedback.\n"
            "Welche Informationen fehlen euch noch?\n"
            "[Schreibt es uns auf Discord](https://discord.gg/7NYgT2uFPm)\n"
            "*⚔ Spieltag 2*\n"
            "[gegen Enemy Team](https://www.primeleague.gg/de/leagues/matches/1)\n\n"

            "*Termin*\n"
            "> 📆 Keine Terminvorschläge. Ausweichtermin: Dienstag, 13. Dezember 2022 23:09 Uhr\n\n"

            "*Gegnerteam*\n"
            "> 🔍 [op.gg](https://euw.op.gg/multisearch/euw?summoners=)\n\n"

            "*Eure Aufstellung*\n"
            "⚠ Es wurde noch kein Lineup aufgestellt.\n\n"

            "*Gegnerische Aufstellung*\n"
            "Es wurde noch kein Lineup aufgestellt.\n\n"

            "*Sonstige Informationen*\n"
            "> Ihr habt im *zweiqten* Match Seitenwahl.\n"
            "> The rulebook is available [here.](https://www.primeleague.gg/statics/rules_general)\n"
        )

        self.assertEqual(expected, response_text)
from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django.test import TestCase, override_settings
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _

from app_prime_league.factories import ChannelFactory, MatchFactory, PlayerFactory, SplitFactory, TeamFactory
from app_prime_league.models import Match
from app_prime_league.models.channel import Languages, Platforms
from bots.telegram_interface.tests.commands.utils import BotMock, test_call_match


@override_settings(
    DEBUG=True,
)
class TelegramMatchTestCase(TestCase):
    TELEGRAM_ID = 1

    def setUp(self) -> None:
        self.bot = BotMock()

    def test_required_match_day_arg_is_missing(self):
        ChannelFactory(platform=Platforms.TELEGRAM, telegram_id=self.TELEGRAM_ID, teams=TeamFactory())
        test_call_match("/match", bot=self.bot)
        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_match_day_arg_has_invalid_format(self):
        ChannelFactory(platform=Platforms.TELEGRAM, telegram_id=self.TELEGRAM_ID, teams=TeamFactory())
        test_call_match("/zwei", bot=self.bot)

        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_match_day_arg_has_invalid_spacing(self):
        ChannelFactory(platform=Platforms.TELEGRAM, telegram_id=self.TELEGRAM_ID, teams=TeamFactory())
        test_call_match("/match 2 2", bot=self.bot)

        self.assertEqual(_("Invalid match day. Try using /match 1."), self.bot.response_text)

    def test_no_registered_team_in_telegram_chat(self):
        test_call_match("/match 3", bot=self.bot)

        self.assertEqual("In der Telegram-Gruppe wurde noch kein Team registriert (/start).", self.bot.response_text)

    def test_at_match_day_are_no_matches(self):
        TeamFactory(name="Team 1", channels=ChannelFactory(platform=Platforms.TELEGRAM, telegram_id=1))
        SplitFactory(group_stage_start=datetime(2022, 1, 1))
        test_call_match("/match 3", bot=self.bot)

        self.assertEqual(_("Sadly there is no match on the given match day."), self.bot.response_text)

    @mock.patch('django.utils.timezone.now')
    def test_existing_match_day_without_lineups(self, timezone_mock):
        timezone_mock.return_value = make_aware(datetime(2022, 1, 30))
        team_1 = TeamFactory(
            name="Team 1",
            channels=ChannelFactory(platform=Platforms.TELEGRAM, telegram_id=1, language=Languages.ENGLISH),
        )
        team_2 = TeamFactory(name="Team 2", players=[PlayerFactory(name="player 2", summoner_name=None)])
        SplitFactory(group_stage_start=datetime(2022, 1, 1))
        MatchFactory(
            match_id=1,
            team=team_1,
            enemy_team=team_2,
            match_day=2,
            match_type=Match.MATCH_TYPE_LEAGUE,
            begin=datetime(2022, 1, 16, 19, 0, tzinfo=ZoneInfo("UTC")),
        )

        test_call_match("/match 2", bot=self.bot)

        expected = (
            "*⚔ Gameday 2*\n"
            "[against Team 2](https://www.primeleague.gg/de/leagues/matches/1)\n\n"
            "*Date*\n"
            "> 📆 No dates proposed. Alternative date: Sunday, 16. January 2022 20:00 PM\n\n"
            "*Opposing team*\n"
            "> 🔍 [op.gg](https://www.op.gg/multisearch/euw?summoners=)\n\n"
            "*Your lineup*\n"
            "⚠ No lineup has been submitted yet.\n\n"
            "*Lineup of opponent*\n"
            "No lineup has been submitted yet.\n\n"
            "*Other information*\n"
            "> You have a choice of sides in the *second* game.\n"
            "> The rulebook is available [here.](https://www.primeleague.gg/statics/rules_general)\n\n"
        )
        self.assertEqual(expected, self.bot.response_text)

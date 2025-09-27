from django.test import TestCase
from django.utils import translation

from app_prime_league.factories import ChannelFactory, MatchFactory, TeamFactory
from app_prime_league.models import Match
from app_prime_league.models.channel import ChannelTeam, Platforms
from bots.messages import NewCommentsNotificationMessage
from core.test_utils import string_to_datetime
from utils.utils import format_datetime


class DiscordMessageTests(TestCase):
    def setUp(self):
        self.team_a = TeamFactory(team_tag="abc", channels=ChannelFactory(platform=Platforms.DISCORD))
        self.team_b = TeamFactory(team_tag="xyz")
        self.match = MatchFactory(
            team=self.team_a, enemy_team=self.team_b, match_day=1, match_id=1, match_type=Match.MatchType.LEAGUE
        )

    def test_i18n(self):
        msg = NewCommentsNotificationMessage(
            channel_team=ChannelTeam.objects.first(),
            match=self.match,
            new_comment_ids=[123],
        )
        result = msg.generate_message()

        expected = (
            "Es gibt [einen neuen Kommentar](https://www.primeleague.gg/de/leagues/matches/1#comment:"
            "123) für [Spieltag 1](https://www.primeleague.gg/de/leagues/"
            f"matches/1) gegen [xyz](https://www.primeleague.gg/de/leagues/teams/{self.team_b.id})."
        )

        self.assertEqual(expected, result)

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

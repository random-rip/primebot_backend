import datetime

import discord
from django.utils.translation import gettext, ngettext

from app_prime_league.models import Match, Team
from bots.messages.base import MatchMessage
from utils.utils import format_datetime


class EnemyNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "ENEMY_SCHEDULING_SUGGESTION"
    settings_key_poll = "ENEMY_SCHEDULING_SUGGESTION_POLL"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team=team, match=match)
        self.details = list(self.match.suggestion_set.all().values_list("begin", flat=True))

    def _generate_title(self):
        return "📆 " + gettext("New date proposed by an opponent")

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))
        enemy_team_tag = self.match.enemy_team.team_tag

        prefix = ngettext(
            "New date proposed by [{enemy_team_tag}]({enemy_team_url}) " "for [{match_day}]({match_url}):",
            "New dates proposed by [{enemy_team_tag}]({enemy_team_url}) " "for [{match_day}]({match_url}):",
            len(details),
        ).format(
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url,
        )

        return (
            prefix
            + "\n"
            + '\n'.join(
                [f"{self._get_number_as_emojis(i)}{format_datetime(x)}" for i, x in enumerate(self.details, start=1)]
            )
        )

    def _generate_poll(self) -> discord.Poll:
        if self.team.value_of_setting(self.settings_key_poll) is False:
            raise Exception
        poll = discord.Poll(
            question="📆 "
            + gettext("Please vote for a new date against {enemy_team_tag}").format(
                enemy_team_tag=self.match.enemy_team.team_tag
            ),
            duration=datetime.timedelta(hours=12),
            multiple=True,
        )
        for i, detail in enumerate(self.details, start=1):
            poll.add_answer(
                text=format_datetime(detail),
                emoji=self._get_number_as_emojis(i),
            )
        poll.add_answer(
            text=gettext("None of the above"),
            emoji="⛔",
        )
        return poll

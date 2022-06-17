from django.utils.translation import gettext, ngettext

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage, emoji_numbers
from utils.utils import format_datetime


class EnemyNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "ENEMY_SCHEDULING_SUGGESTION"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)

    def _generate_title(self):
        return f"📆 {gettext('Neuer Terminvorschlag eines Gegners')}"

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))
        enemy_team_tag = self.match.enemy_team.team_tag

        prefix = ngettext(
            "Neuer Terminvorschlag von [{enemy_team_tag}]({enemy_team_url}) für [{match_day}]({match_url}):",
            "Neue Terminvorschläge von [{enemy_team_tag}]({enemy_team_url}) für [{match_day}]({match_url}):",
            len(details)
        ).format(
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.helper.display_match_day(self.match),
            match_url=self.match_url
        )

        return prefix + "\n" + '\n'.join(
            [f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])

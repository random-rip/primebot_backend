from django.utils.translation import gettext, ngettext

from bots.messages.base import MatchMessage, emoji_numbers
from utils.utils import format_datetime


class EnemyNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "ENEMY_SCHEDULING_SUGGESTION"
    mentionable = True

    def __init__(self, team_id: int, match_id: int):
        super().__init__(team_id=team_id, match_id=match_id)

    def _generate_title(self):
        return "📆 " + gettext("New date proposed by an opponent")

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))
        enemy_team_tag = self.match.enemy_team.team_tag

        prefix = ngettext(
            "New date proposed by [{enemy_team_tag}]({enemy_team_url}) "
            "for [{match_day}]({match_url}):"
            ,
            "New dates proposed by [{enemy_team_tag}]({enemy_team_url}) "
            "for [{match_day}]({match_url}):"
            ,
            len(details)
        ).format(
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url
        )

        return prefix + "\n" + '\n'.join(
            [f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])

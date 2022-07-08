from django.utils.translation import gettext as _

from bots.messages.base import MatchMessage


class NewLineupNotificationMessage(MatchMessage):
    settings_key = "LINEUP_NOTIFICATION"
    mentionable = True

    def __init__(self, team_id: int, match_id: int):
        super().__init__(team_id=team_id, match_id=match_id)

    def _generate_title(self):
        return "📑 " + _("New lineup")

    def _generate_message(self):
        return _(
            "[{enemy_team_tag}]({enemy_team_url}) ([{match_day}]({match_url})) "
            "submitted a new [lineup]({scouting_url})."
        ).format(
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url,
            scouting_url=self.enemy_lineup_scouting_url,
        )

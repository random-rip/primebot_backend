from django.utils.translation import gettext, ngettext

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage


class NewCommentsNotificationMessage(MatchMessage):
    settings_key = "NEW_COMMENTS_OF_UNKNOWN_USERS"
    mentionable = True

    def __init__(self, team: Team, match: Match, new_comment_ids):
        super().__init__(team, match)
        self.new_comment_ids = new_comment_ids

    def _generate_title(self):
        return f"💬 {gettext('Neue Kommentare')}"

    def _generate_message(self):
        enemy_team_tag = self.match.enemy_team.team_tag
        message = ngettext(
            "Es gibt [einen neuen Kommentar]({match_url}) für [{match_day}]({match_url}) gegen "
            "[{enemy_team_tag}]({enemy_team_url}). 💬",
            "Es gibt [neue Kommentare]({match_url}) für [{match_day}]({match_url}) gegen "
            "[{enemy_team_tag}]({enemy_team_url}). 💬",
            len(self.new_comment_ids)
        )

        return gettext(message).format(
            match_day=self.helper.display_match_day(self.match),
            enemy_team_tag=enemy_team_tag,
            match_url=f"{self.match_url}#comment:{self.new_comment_ids[0]}",
            enemy_team_url=self.enemy_team_url,
        )

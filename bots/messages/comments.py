from django.utils.translation import gettext, ngettext

from bots.messages.base import MatchMessage


class NewCommentsNotificationMessage(MatchMessage):
    settings_key = "NEW_COMMENTS_OF_UNKNOWN_USERS"
    mentionable = True

    def __init__(self, team_id: int, match_id: int, new_comment_ids):
        super().__init__(team_id=team_id, match_id=match_id)
        self.new_comment_ids = new_comment_ids

    def _generate_title(self):
        return "💬 " + gettext('New comments')

    def _generate_message(self):
        enemy_team_tag = self.match.enemy_team.team_tag
        message = ngettext(
            "There is [a new comment]({match_url}) for [{match_day}]({match_url}) "
            "against [{enemy_team_tag}]({enemy_team_url}).",
            "There are [new comments]({match_url}) for [{match_day}]({match_url}) "
            "against [{enemy_team_tag}]({enemy_team_url}).",
            len(self.new_comment_ids)
        )

        return gettext(message).format(
            match_day=self.match_helper.display_match_day(self.match),
            enemy_team_tag=enemy_team_tag,
            match_url=f"{self.match_url}#comment:{self.new_comment_ids[0]}",
            enemy_team_url=self.enemy_team_url,
        )

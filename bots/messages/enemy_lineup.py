import discord
from django.utils.translation import gettext as _

from bots.discord_interface.utils import COLOR_NOTIFICATION
from bots.messages.base import MatchMessage


class NewLineupNotificationMessage(MatchMessage):
    settings_key = "LINEUP_NOTIFICATION"
    mentionable = True

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

    def _generate_discord_embed(self) -> discord.Embed:
        embed = discord.Embed(color=COLOR_NOTIFICATION)
        embed.add_field(name="", value=self._generate_message(), inline=False)
        embed.set_footer(text=_("To get more information about the match, use /match."))
        return embed

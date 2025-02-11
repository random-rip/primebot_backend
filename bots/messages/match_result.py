import discord
from django.utils.translation import gettext

from bots.discord_interface.utils import COLOR_NOTIFICATION
from bots.messages.base import MatchMessage


class MatchResultMessage(MatchMessage):
    settings_key = "MATCH_RESULT"
    mentionable = True

    def _generate_title(self):
        return "🏆 " + gettext('Match result')

    def _generate_message(self):
        enemy_team_tag = self.match.enemy_team.team_tag
        message = gettext("The match against [{enemy_team_tag}]({enemy_team_url}) ended with **{result}**.")

        return message.format(
            match_day=self.match_helper.display_match_day(self.match),
            enemy_team_tag=enemy_team_tag,
            match_url=self.match_url,
            enemy_team_url=self.enemy_team_url,
            result=self.match.result,
        )

    def _generate_discord_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=self._generate_title(),
            color=COLOR_NOTIFICATION,
        )
        embed.add_field(name="", value=self._generate_message(), inline=False)
        team_score, enemy_team_score = self.match.result.split(":")
        if team_score >= enemy_team_score:
            footer_text = gettext("To get more information about the match, use /match.")
        else:
            footer_text = gettext("Sad, but maybe /bop will cheer you up.")
        embed.set_footer(
            text=footer_text,
        )
        return embed

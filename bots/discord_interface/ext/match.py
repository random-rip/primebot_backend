import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, ChannelTeam, Team
from bots.discord_interface.ui.buttons import BackButton, BaseMatchButton, CloseButton
from bots.discord_interface.ui.views import BaseTeamSelectionView, BaseView
from bots.discord_interface.utils import channel_has_at_least_one_team, channel_is_registered, translation_override
from bots.messages import MatchOverview


class MatchButton(BaseMatchButton):

    @translation_override
    async def callback(self, interaction: discord.Interaction):
        msg = await sync_to_async(MatchOverview)(channel_team=self.channel_team, match=self.match)
        embed = await sync_to_async(msg.generate_discord_embed)()
        await interaction.response.edit_message(
            content=None,
            embed=embed,
        )


class MatchSelectionView(BaseView):
    def __init__(self, _matches, channel_team, teams=None, **kwargs):
        super().__init__(**kwargs)
        self.matches = _matches
        self.channel = channel_team.channel
        self.channel_team = channel_team
        self.teams = teams

    async def build(self):
        for _match in self.matches:
            self.add_item(MatchButton(match=_match, channel_team=self.channel_team))
        if self.teams is not None and len(self.teams) > 1:
            self.add_item(BackButton(self.teams, self._back, row=4))
        self.add_item(CloseButton(row=4))

    @translation_override
    async def _back(self, interaction: discord.Interaction):
        self.stop()
        view = MatchTeamSelectionView(teams=self.teams, channel=self.channel, message=self.message)
        await view.build()
        await interaction.response.edit_message(
            content=_("Select a team"),
            view=view,
            embed=None,
        )


class MatchTeamSelectionView(BaseTeamSelectionView):

    @translation_override
    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction):
        self.stop()
        found_matches_query = await sync_to_async(team.get_obvious_matches_based_on_stage)(match_day=None)
        found_matches = await sync_to_async(list)(found_matches_query.order_by("match_day", "begin"))
        channel_team = await ChannelTeam.objects.select_related("channel", "team").aget(channel=self.channel, team=team)
        view = MatchSelectionView(
            _matches=found_matches, channel_team=channel_team, teams=self.teams, message=self.message
        )
        await view.build()
        content = _("Select a match") if len(found_matches) > 0 else _("No matches found")
        await interaction.response.edit_message(content=content, view=view)


@commands.hybrid_command(name="match", help=_("Create an overview for a specific match day"))
@commands.guild_only()
@channel_is_registered()
@channel_has_at_least_one_team()
@translation_override
async def match(ctx):
    channel = await Channel.objects.aget(discord_channel_id=ctx.message.channel.id)
    teams = await sync_to_async(list)(Team.objects.filter(channels=channel).order_by("name"))
    if len(teams) == 1:
        found_matches_query = await sync_to_async(teams[0].get_obvious_matches_based_on_stage)(match_day=None)
        found_matches = await sync_to_async(list)(found_matches_query.order_by("match_day", "begin"))
        channel_team = await ChannelTeam.objects.select_related("channel", "team").aget(channel=channel, team=teams[0])
        view = MatchSelectionView(_matches=found_matches, channel_team=channel_team)
        await view.build()
        message = await ctx.send(view=view)
        view.message = message
        return

    view = MatchTeamSelectionView(teams=teams, channel=channel)
    await view.build()
    message = await ctx.send(
        content=_("Select a team"),
        view=view,
    )
    view.message = message


async def setup(bot: commands.Bot) -> None:
    bot.add_command(match)

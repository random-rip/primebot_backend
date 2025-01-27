import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, ChannelTeam, Team
from bots.discord_interface.ui.views import BaseTeamSelectionView
from bots.discord_interface.utils import channel_has_at_least_one_team, channel_is_registered, translation_override
from bots.messages import MatchesOverview


class TeamSelectionView(BaseTeamSelectionView):
    @translation_override
    async def handle_team_select(self, team: Team, interaction: discord.Interaction, view):
        channel_team = await ChannelTeam.objects.aget(channel=self.channel, team=team)
        msg = await sync_to_async(MatchesOverview)(channel_team=channel_team, match_ids=None)
        embed = await sync_to_async(msg.generate_discord_embed)()
        view = TeamSelectionView(teams=self.teams, channel=self.channel, selected_team=team)
        await view.build()
        await interaction.response.edit_message(
            content=None,
            view=view,
            embed=embed,
        )


@commands.hybrid_command(help="Creates an overview for open matches")
@commands.guild_only()
@channel_is_registered()
@channel_has_at_least_one_team()
@translation_override
async def matches(ctx):
    channel = await Channel.objects.aget(discord_channel_id=ctx.message.channel.id)
    teams = await sync_to_async(list)(Team.objects.filter(channels=channel).order_by("name"))
    if len(teams) == 1:
        async with ctx.typing():
            channel_team = await ChannelTeam.objects.aget(channel=channel, team=teams[0])
            msg = await sync_to_async(MatchesOverview)(channel_team=channel_team, match_ids=None)
            embed = await sync_to_async(msg.generate_discord_embed)()
        await ctx.send(embed=embed)
        return

    view = TeamSelectionView(teams=teams, channel=channel)
    await view.build()
    await ctx.send(content=_("Select a team"), view=view)


async def setup(bot: commands.Bot) -> None:
    bot.add_command(matches)

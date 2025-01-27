import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, ChannelTeam, Team
from bots.discord_interface.ui.buttons import BackButton, CloseButton
from bots.discord_interface.ui.utils import shorten_team_name
from bots.discord_interface.ui.views import BaseTeamSelectionView
from bots.discord_interface.utils import DiscordHelper, channel_is_registered, check_channel_type, translation_override


class DeleteButton(discord.ui.Button):
    def __init__(self, team, channel, **kwargs):
        kwargs.setdefault("style", discord.ButtonStyle.danger)
        shortened_team_name = shorten_team_name(team.name)
        kwargs.setdefault("label", _("Remove {team_name} from Channel").format(team_name=shortened_team_name))
        self.team = team
        self.channel = channel
        super().__init__(**kwargs)

    @translation_override
    async def callback(self, interaction: discord.Interaction):
        channel_team = await ChannelTeam.objects.aget(channel=self.channel, team=self.team)
        await sync_to_async(Team.objects.cleanup)(channel_team)

        await interaction.response.edit_message(
            delete_after=0,
        )

        await interaction.followup.send(
            _("The team {team_name} has been removed from the channel.").format(team_name=self.team.name),
        )

        if await self.channel.teams.aexists():
            return

        # No team is registered in the channel anymore
        await interaction.followup.send(
            _("All teams have been removed from the channel, so I clean up the remaining channel settings for you. 🧹"),
        )

        await DiscordHelper.delete_webhooks(interaction.channel)
        await self.channel.adelete()
        await interaction.followup.send(
            _(
                "All deleted. Feel free to give us feedback on {discord_link} if you are missing or don't like any "
                "functionality. Bye! ✌\n"
            ).format(discord_link=settings.DISCORD_SERVER_LINK)
        )


class ConfirmView(discord.ui.View):
    def __init__(self, channel: Channel, team: Team, teams=None):
        super().__init__()
        self.channel = channel
        self.team = team
        self.teams = teams

    async def build(self):
        self.add_item(DeleteButton(team=self.team, channel=self.channel))
        self.add_item(BackButton(teams=self.teams, callback=self._back, row=4))
        self.add_item(CloseButton(row=4))

    @translation_override
    async def _back(self, interaction: discord.Interaction):
        view = DeleteView(teams=self.teams, channel=self.channel)
        await view.build()
        await interaction.response.edit_message(content=_("Select a team"), view=view)


class DeleteView(BaseTeamSelectionView):

    @translation_override
    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction, view):
        view = ConfirmView(channel=self.channel, team=team, teams=self.teams)
        await view.build()
        await interaction.response.edit_message(
            content=None,
            view=view,
        )


@commands.hybrid_command(help=_("Remove the team from the channel"))
@commands.guild_only()
@channel_is_registered()
@check_channel_type()
@translation_override
async def delete(ctx):
    channel_id = ctx.message.channel.id
    channel = await Channel.objects.aget(discord_channel_id=channel_id)
    teams = await sync_to_async(list)(Team.objects.filter(channels=channel).order_by("name"))
    selected_team = teams[0] if len(teams) == 1 else None
    view = DeleteView(teams=teams, channel=channel, selected_team=selected_team)
    await view.build()
    await ctx.send(
        content=_("Select a team"),
        view=view,
        ephemeral=True,
        delete_after=60 * 5,
    )


async def setup(bot: commands.Bot) -> None:
    bot.add_command(delete)

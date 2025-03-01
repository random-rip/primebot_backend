import typing
from typing import Iterable

import discord
from asgiref.sync import sync_to_async
from discord import SelectDefaultValue, SelectDefaultValueType
from discord.ext import commands
from discord.role import Role
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, ChannelTeam, Team
from bots.discord_interface.ui.buttons import BackButton, CloseButton
from bots.discord_interface.ui.views import BaseTeamSelectionView, BaseView
from bots.discord_interface.utils import channel_has_at_least_one_team, channel_is_registered, translation_override


class RoleSelect(discord.ui.RoleSelect):
    def __init__(self, callback: typing.Callable[[Iterable, discord.Interaction], typing.Coroutine], **kwargs):
        self._callback = callback
        super().__init__(placeholder=_("Select a role"), min_values=0, max_values=1, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await self._callback(self.values, interaction)


class RoleSelectionView(BaseView):
    def __init__(self, channel_team: ChannelTeam, teams: list[Team] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.channel_team = channel_team
        self.channel = channel_team.channel
        self.teams = teams

    async def _selection_callback(self, values, interaction: discord.Interaction):
        selected: Role = values[0] if values else None
        if not selected:
            self.channel_team.discord_role_id = None
            await self.channel_team.asave()
            await interaction.response.edit_message(
                content=_(
                    _("All right, I've removed the role for the team **{team_name}**.").format(
                        team_name=self.channel_team.team.name
                    )
                )
            )
            return

        self.channel_team.discord_role_id = selected.id
        await self.channel_team.asave()
        await interaction.response.edit_message(
            content=_("Okay, I'll  inform the team **{team_name}** with the role **{role_name}** 📯").format(
                role_name=selected.name, team_name=self.channel_team.team.name
            )
        )

    async def build(self):
        defaults = []
        if self.channel_team.discord_role_id is not None:
            defaults.append(
                SelectDefaultValue(id=int(self.channel_team.discord_role_id), type=SelectDefaultValueType.role)
            )
        self.add_item(
            RoleSelect(
                default_values=defaults,
                row=0,
                callback=self._selection_callback,
            )
        )
        if self.teams is not None and len(self.teams) > 1:
            self.add_item(BackButton(self.teams, self._back, row=4))
        self.add_item(CloseButton(row=4))

    @translation_override
    async def _back(self, interaction: discord.Interaction):
        self.stop()
        view = RoleTeamSelectionView(teams=self.teams, channel=self.channel, message=self.message)
        await view.build()
        await interaction.response.edit_message(
            content=_("Select a team for which you want to set a role or update the role for all teams."),
            view=view,
            embed=None,
        )


class BulkRoleSelectionView(BaseView):
    def __init__(self, channel: Channel, teams: list[Team], **kwargs):
        super().__init__(**kwargs)
        self.channel = channel
        self.teams = teams

    async def build(self):
        self.add_item(
            RoleSelect(
                callback=self._selection_callback,
                row=0,
            )
        )
        self.add_item(BackButton(self.teams, self._back, row=4))
        self.add_item(CloseButton(row=4))

    @translation_override
    async def _back(self, interaction: discord.Interaction):
        self.stop()
        view = RoleTeamSelectionView(teams=self.teams, channel=self.channel, message=self.message)
        await view.build()
        await interaction.response.edit_message(
            content=_("Select a team for which you want to set a role or update the role for all teams."),
            view=view,
            embed=None,
        )

    async def _selection_callback(self, values, interaction: discord.Interaction):
        selected: Role = values[0] if values else None
        if not selected:
            await self.channel.channel_teams.aupdate(discord_role_id=None)
            await interaction.response.edit_message(content=_("Alright, I've removed the roles for all teams."))
            return

        await self.channel.channel_teams.aupdate(discord_role_id=selected.id)
        await interaction.response.edit_message(
            content=_("Okay, I'll inform all teams with the role **{role_name}** 📯").format(role_name=selected.name)
        )


class BulkUpdateRoleButton(discord.ui.Button):
    def __init__(self, channel: Channel, **kwargs):
        kwargs["style"] = discord.ButtonStyle.secondary
        kwargs["label"] = _("Update all teams at once")
        self.channel = channel
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.stop()
        teams = await sync_to_async(list)(Team.objects.filter(channels=self.channel).order_by("name"))
        view = BulkRoleSelectionView(channel=self.channel, teams=teams, message=self.view.message)
        await view.build()
        await interaction.response.edit_message(
            content=_("Select a role or remove the roles for all teams."),
            view=view,
        )


class RoleTeamSelectionView(BaseTeamSelectionView):

    async def build(self):
        await super().build()
        self.add_item(BulkUpdateRoleButton(self.channel, row=3))

    @translation_override
    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction):
        self.stop()
        channel_team = await ChannelTeam.objects.select_related("channel", "team").aget(channel=self.channel, team=team)
        view = RoleSelectionView(channel_team=channel_team, teams=self.teams, message=self.message)
        await view.build()
        await interaction.response.edit_message(
            content=_("Select a role or remove the role for the team **{team_name}**.").format(team_name=team.name),
            view=view,
        )


@commands.hybrid_command(name="role", help=_("Set a Discord role that will be used in notifications"))
@commands.guild_only()
@channel_is_registered()
@channel_has_at_least_one_team()
@translation_override
async def set_role(
    ctx,
):
    channel = await Channel.objects.aget(discord_channel_id=ctx.message.channel.id)
    teams = await sync_to_async(list)(Team.objects.filter(channels=channel).order_by("name"))
    if len(teams) == 1:
        channel_team = await ChannelTeam.objects.select_related("channel", "team").aget(channel=channel, team=teams[0])
        view = RoleSelectionView(channel_team=channel_team)
        await view.build()
        message = await ctx.send(view=view)
        view.message = message
        return

    view = RoleTeamSelectionView(teams=teams, channel=channel)
    await view.build()
    message = await ctx.send(
        content=_("Select a team for which you want to set a role or update the role for all teams."),
        view=view,
        ephemeral=True,
        delete_after=60 * 10,
    )
    view.message = message


async def setup(bot: commands.Bot) -> None:
    bot.add_command(set_role)

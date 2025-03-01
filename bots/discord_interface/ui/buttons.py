from typing import Any, Callable, Coroutine

import discord
from discord import Interaction
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, Team
from bots.discord_interface.ui.utils import shorten_team_name
from bots.messages.helpers import MatchDisplayHelper


class BaseMatchButton(discord.ui.Button):
    def __init__(self, match, channel_team, **kwargs):
        if match.closed is True:
            kwargs["style"] = discord.ButtonStyle.secondary
        else:
            kwargs["style"] = discord.ButtonStyle.success
        kwargs["label"] = MatchDisplayHelper.display_match_day(match)
        self.match = match
        self.channel_team = channel_team
        super().__init__(**kwargs)


class BaseTeamButton(discord.ui.Button):
    def __init__(self, team: Team, channel: Channel, **kwargs):
        kwargs.setdefault("style", discord.ButtonStyle.secondary)
        shortened_team_name = shorten_team_name(team.name, max_length=80)
        kwargs.setdefault("label", shortened_team_name)
        self.team = team
        self.channel = channel
        super().__init__(**kwargs)

    async def callback(self, interaction: Interaction) -> Any:
        await self.view.handle_team_select(self.team, interaction)


class BackButton(discord.ui.Button):
    def __init__(self, teams, callback: Callable[[discord.Interaction], Coroutine], **kwargs):
        kwargs["style"] = discord.ButtonStyle.primary
        kwargs["label"] = _("Back")
        self.teams = teams
        self._callback = callback
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction)


class CloseButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = discord.ButtonStyle.primary
        kwargs["label"] = _("Close")
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=_("Done."),
            view=None,
        )

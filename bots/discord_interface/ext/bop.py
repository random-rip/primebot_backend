import logging
from io import BytesIO
from typing import List

import aiohttp
import discord
from asgiref.sync import sync_to_async
from discord import SelectOption, Member, User, Role, Object
from discord.ext import commands
from discord.ui import RoleSelect
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.base.bop import GIFinator
from bots.discord_interface.utils import translation_override

class MentionSelect(discord.ui.MentionableSelect):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: MentionSelectView = self.view
        await view.handle_mention_select(self.values[0], interaction)


merlin = Object(id=249255059836108800, type=Member) # TODO @janek replace mit actual mention und so

class MentionSelectView(discord.ui.View):
    def __init__(self, teams: List[Team] = None, default_team: Team = None, default_mention: Member | User | Role  = None):
        super().__init__()
        self.default_mention = default_mention
        self.default_team = default_team
        self.team_options = teams or []
        self.selected_team = default_team
        self.create_team_select(teams=teams, default=default_team)
        self.create_mention_select(default_values=[default_mention])

    def create_team_select(self, teams: List[Team], **kwargs):
        kwargs.setdefault("disabled",(self.default_team is not None))
        self.add_item(SettingsViewTeamSelect(options=teams, **kwargs))

    def create_mention_select(self, **kwargs):
        kwargs.setdefault("disabled",(self.default_team is None))
        kwargs.setdefault("default_values",([self.default_mention]))
        self.add_item(MentionSelect(**kwargs))

    async def handle_mention_select(self, role: Member | User | Role ,interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Mentioned: " + role.mention + " for " + self.selected_team.name, view=self)
        pass # todo @janek implement


    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction):
        self.clear_items()
        self.selected_team = team
        await interaction.response.edit_message(view=MentionSelectView(teams=self.team_options,default_team=team, default_mention=self.default_mention))
        pass


class OpenSettingsButton(discord.ui.Button):
    def __init__(self, url, **kwargs):
        kwargs.setdefault("disabled",False)
        kwargs.setdefault("label", "Settings")
        super().__init__(url=url, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=SettingsView(), ephemeral=True)


class ChangeTeamButton(discord.ui.Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("disabled",False)
        kwargs.setdefault("label", "Team ändern")
        kwargs.setdefault("style", discord.ButtonStyle.secondary)
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: SettingsView = self.view
        await view.handle_team_select(None, interaction)

class SettingsViewTeamSelect(discord.ui.Select['SettingsView']):
    def __init__(self, options: List[Team], default: Team = None, **kwargs):
        team_options = [SelectOption(label=team.name, value=f'{team.id}', default=(default and team.id == default.id)) for team in options]
        kwargs.setdefault("placeholder","Select your team", )
        super().__init__(min_values=1, max_values=1, options=team_options,**kwargs)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: SettingsView = self.view
        selected_team = await sync_to_async(Team.objects.get)(id=int(self.values[0]))
        if selected_team:
            await view.handle_team_select(team=selected_team, interaction=interaction)

class SettingsView(discord.ui.View):
    def __init__(self, teams: List[Team], selected_team: Team = None):
        assert len(teams) > 0
        super().__init__()
        self.selected_team = teams[0] or selected_team
        self.team_options = teams or []
        self.create_team_select(teams)
        self.create_settings_link_button()
        self.create_change_team_button()

    def create_team_select(self, teams: List[Team], **kwargs):
        kwargs.setdefault("disabled",(self.selected_team is not None))
        self.add_item(SettingsViewTeamSelect(options=teams, default=self.selected_team, **kwargs))

    def create_settings_link_button(self, **kwargs):
        kwargs.setdefault("disabled",(self.selected_team is None))
        self.add_item(OpenSettingsButton(url="https://google.com",**kwargs)) # todo team url

    def create_change_team_button(self, **kwargs):
        kwargs.setdefault("disabled", self.selected_team is None)
        self.add_item(ChangeTeamButton(**kwargs))

    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction):
        self.clear_items()
        await interaction.response.edit_message(view=SettingsView(teams=self.team_options, selected_team=team))

@commands.hybrid_command(
    help="What's boppin'?",
)
async def bop(
    ctx: commands.Context,
) -> None:
    teams = await sync_to_async(list)(Team.objects.all())
    await ctx.send(view=MentionSelectView(teams=teams,default_team=None, default_mention=merlin), ephemeral=True)
    # await ctx.interaction.response.send_modal(Feedback())
    # async with ctx.typing():
    #     try:
    #         # send modal with text field
    #
    #         url = GIFinator.get_gif()
    #     except ConnectionError:
    #         return await ctx.send(_("It's not my fault, but I can't get you your surprise. :("))
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as resp:
    #             buffer = BytesIO(await resp.read())
    # await ctx.send(file=discord.File(fp=buffer, filename="bop.gif"))


@bop.error
@translation_override
async def bop_error(ctx, error):
    if isinstance(error, ConnectionError):
        await ctx.send(_("It's not my fault, but I can't get you your surprise. :("))
    logging.getLogger("commands").exception(error)
    return await ctx.reply(
        _("An unknown error has occurred. Please contact the developers on Discord at {discord_link}.").format(
            discord_link=settings.DISCORD_SERVER_LINK
        ),
        suppress_embeds=True,
    )


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bop)

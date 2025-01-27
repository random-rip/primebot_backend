import discord
from django.utils.translation import gettext as _

from app_prime_league.models import Team


class BaseTeamSelect(discord.ui.Select):
    def __init__(self, options: list[Team], default: Team = None, **kwargs):
        team_options = [
            discord.SelectOption(label=team.name, value=f'{team.id}', default=(default and team.id == default.id))
            for team in options
        ]
        kwargs.setdefault(
            "placeholder",
            _("Select a team"),
        )
        super().__init__(min_values=1, max_values=1, options=team_options, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        selected_team = await Team.objects.aget(id=int(self.values[0]))
        await self.view.handle_team_select(team=selected_team, interaction=interaction, view=self.view)


class MentionSelect(discord.ui.MentionableSelect):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        pass
        # assert self.view is not None
        # view: MentionSelectView = self.view
        # await view.handle_mention_select(self.values[0], interaction)

import discord

from app_prime_league.models import Channel, Team

from .buttons import BaseTeamButton, CloseButton
from .selects import BaseTeamSelect


class BaseTeamSelectionView(discord.ui.View):
    """Creates a button for each team (up to 5) or a Select-Menu for more than 5 teams"""

    def __init__(self, teams: list[Team], channel: Channel, selected_team: Team | None = None):
        super().__init__()
        self.teams = teams
        self.channel = channel
        self.selected_team = selected_team

    @property
    def is_select(self):
        return len(self.teams) > 2

    async def build(self):
        if self.is_select:
            self.add_item(
                BaseTeamSelect(
                    options=self.teams,
                    default=self.selected_team,
                    row=0,
                )
            )
        else:
            for team in self.teams:
                self.add_item(
                    BaseTeamButton(
                        team=team,
                        channel=self.channel,
                        row=0,
                    )
                )
        self.add_item(CloseButton(row=4))

    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction, view):
        pass

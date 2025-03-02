import logging
from abc import ABC, abstractmethod

import discord

from app_prime_league.models import Channel, Team

from .buttons import BaseTeamButton, CloseButton
from .selects import BaseTeamSelect

VIEW_TIMEOUT_SECONDS = 60


class BaseView(discord.ui.View, ABC):
    """
    Handles timeouts properly. Make sure to pass the message attribute to the view either
    in the constructor or by setting it after the message has been sent.

    Example:
    ::

        def command(ctx):
            view = MyView()
            await view.build()
            message = await ctx.send(view=view)
            view.message = message
        # or
        async def handle(self, interaction: discord.Interaction, view: BaseView):
            view = MyView(message=view.message)
            await view.build()
            await interaction.response.edit_message(view=view)
    """

    def __init__(self, message=None, **kwargs):
        kwargs.setdefault("timeout", VIEW_TIMEOUT_SECONDS)
        super().__init__(**kwargs)
        self.message = message

    async def on_timeout(self) -> None:
        if self.message is None:
            logging.getLogger("discord").warning(
                f"View {self.__class__.__name__} has no message attribute. Cannot disable buttons."
            )
            return
        for item in self.children:
            item.disabled = True
        await self.message.edit(
            view=self,
        )

    @abstractmethod
    async def build(self):
        pass


class BaseTeamSelectionView(BaseView):
    """Creates a button for each team (up to 4) or a Select-Menu for more than 4 teams"""

    def __init__(self, teams: list[Team], channel: Channel, selected_team: Team | None = None, **kwargs):
        super().__init__(**kwargs)
        self.teams = teams
        self.channel = channel
        self.selected_team = selected_team

    @property
    def is_select(self):
        return len(self.teams) > 1

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

    async def handle_team_select(self, team: Team | None, interaction: discord.Interaction):
        """
        Override this method to handle the team selection. However, don't forget to call
        `self.stop()` if you want to create and send a new the view. Then `on_timeout()` must be handled properly.
        """

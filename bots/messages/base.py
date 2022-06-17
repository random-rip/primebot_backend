from abc import abstractmethod, ABC

import discord
from django.conf import settings
from django.utils import translation

from app_prime_league.models import Team, Match
from bots.messages.helpers import MatchDisplayHelper
from utils.emojis import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_FOUR, EMOJI_FIVE, EMOJI_SIX, EMOJI_SEVEN, EMOJI_EIGHT, \
    EMOJI_NINE, EMOJI_TEN

emoji_numbers = [
    EMOJI_ONE,
    EMOJI_TWO,
    EMOJI_THREE,
    EMOJI_FOUR,
    EMOJI_FIVE,
    EMOJI_SIX,
    EMOJI_SEVEN,
    EMOJI_EIGHT,
    EMOJI_NINE,
    EMOJI_TEN,
]


class MessageNotImplementedError(NotImplementedError):
    def __init__(self):
        super().__init__("This kind of message is not implemented.")


class BaseMessage:
    settings_key = None  # Message kann über die Settings gesteuert werden, ob sie gesendet wird, oder nicht
    mentionable = False  # Rollenerwähnung bei discord falls Rolle gesetzt

    def __init__(self, team: Team, **kwargs):
        self.team = team
        self.helper = MatchDisplayHelper

    @abstractmethod
    def _generate_title(self) -> str:
        pass

    def generate_title(self) -> str:
        with translation.override(self.team.language):
            return self._generate_title()

    @abstractmethod
    def _generate_message(self) -> str:
        pass

    def generate_message(self) -> str:
        with translation.override(self.team.language):
            return self._generate_message()

    def _generate_discord_embed(self) -> discord.Embed:
        raise MessageNotImplementedError()

    def generate_discord_embed(self) -> discord.Embed:
        with translation.override(self.team.language):
            return self._generate_discord_embed()

    def team_wants_notification(self):
        key = type(self).settings_key
        if key is None:
            return True
        return self.team.value_of_setting(key)

    @property
    def scouting_website(self):
        return settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name


class MatchMessage(BaseMessage, ABC):

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match

    @property
    def match_url(self):
        return f"{settings.MATCH_URI}{self.match.match_id}"

    @property
    def enemy_team_url(self):
        return f"{settings.TEAM_URI}{self.match.enemy_team_id}"

    @property
    def enemy_team_scouting_url(self):
        return self.team.get_scouting_url(match=self.match, lineup=False)

    @property
    def enemy_lineup_scouting_url(self):
        return self.team.get_scouting_url(match=self.match, lineup=True)

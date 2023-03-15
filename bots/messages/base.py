from abc import abstractmethod, ABC
from typing import List

import discord
from django.conf import settings
from django.utils import translation

from app_prime_league.models import Team, Match
from bots.messages.helpers import MatchDisplayHelper
from utils import emojis
from utils.emojis import EMOJI_RAUTE

NUMBER_TO_EMOJI = {
    0: emojis.EMOJI_ZERO,
    1: emojis.EMOJI_ONE,
    2: emojis.EMOJI_TWO,
    3: emojis.EMOJI_THREE,
    4: emojis.EMOJI_FOUR,
    5: emojis.EMOJI_FIVE,
    6: emojis.EMOJI_SIX,
    7: emojis.EMOJI_SEVEN,
    8: emojis.EMOJI_EIGHT,
    9: emojis.EMOJI_NINE,
}


class MessageNotImplementedError(NotImplementedError):
    def __init__(self):
        super().__init__("This kind of message is not implemented.")


class BaseMessage:
    settings_key = None  # Message kann über die Settings gesteuert werden, ob sie gesendet wird, oder nicht
    mentionable = False  # Rollenerwähnung bei discord falls Rolle gesetzt

    def __init__(self, team: Team, **kwargs):
        self.team = team
        self.match_helper = MatchDisplayHelper

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

    def _get_number_as_emojis(self, number: int) -> str:
        return "".join([NUMBER_TO_EMOJI.get(int(d), EMOJI_RAUTE) for d in str(number)])

    def __repr__(self):
        return self.__class__.__name__


class MatchMixin:
    def get_match_url(self, match: Match):
        return f"{settings.MATCH_URI}{match.match_id}"

    def get_enemy_team_url(self, match: Match):
        return f"{settings.TEAM_URI}{match.enemy_team_id}"

    def get_enemy_team_scouting_url(self, match: Match):
        return self.team.get_scouting_url(match=match, lineup=False)

    def get_enemy_lineup_scouting_url(self, match: Match):
        return self.team.get_scouting_url(match=match, lineup=True)


class MatchMessage(BaseMessage, ABC, MatchMixin):
    def __init__(self, team: Team, match: Match):
        super().__init__(team=team)
        self.match = match

    @property
    def match_url(self):
        return self.get_match_url(match=self.match)

    @property
    def enemy_team_url(self):
        return self.get_enemy_team_url(match=self.match)

    @property
    def enemy_team_scouting_url(self):
        return self.get_enemy_team_scouting_url(self.match)

    @property
    def enemy_lineup_scouting_url(self):
        return self.get_enemy_lineup_scouting_url(self.match)


class MatchesMessage(BaseMessage, ABC, MatchMixin):
    def __init__(self, team: Team, matches: List[Match]):
        super().__init__(team=team)
        self.matches = matches

    @abstractmethod
    def header(self) -> str:
        """
        Header of the message before the ``matches`` are listed:

        **<Your header here>**
            - <Match 1>
            - ...
        """

    @abstractmethod
    def no_matches_found(self) -> str:
        """
        Message if ``matches`` is an empty list.
        """

    @abstractmethod
    def format_match(self, match) -> str:
        """
        Format the ``match``. This method will be called while iterating over ``matches``.

        Returns: String formatted match

        """

    def _generate_message(self):
        if len(self.matches) == 0:
            return self.no_matches_found()
        a = [f"{self.format_match(match)}\n" for match in self.matches]
        matches_text = "\n".join(a)
        return f"**" + self.header() + f"**\n\n{matches_text}"

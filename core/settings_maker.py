import logging
from datetime import datetime, timedelta
from urllib import parse

import cryptography
from cryptography.fernet import Fernet
from dateutil.parser import ParserError
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app_prime_league.models import ChannelTeam, ScoutingWebsite, SettingsExpiring
from app_prime_league.models.channel import Platforms
from utils.utils import Encoder

MALFORMED_REQUEST = "invalid_request"
MALFORMED_TEAM = "invalid_team"
MALFORMED_DATE = "invalid_date"
MALFORMED_PLATFORM = "invalid_platform"
MALFORMED_CONTENT = "invalid_content"
MISSING_CONTENT = "missing_content"
EXPIRED_DATE = "url_expired"


class SettingsMaker(Encoder):
    """
    Class to handle the whole cryptography logic, encoding and decoding data, validating data and creating temporary
    links. Set `team` or `data` in initialization.
    """

    key_channel_team = "enc"
    key_validation_hash = "hash"
    key_expiring_at = "expiring_at"
    key_platform = "platform"
    key_content = "settings"

    def __init__(self, **kwargs):
        self.channel_team: ChannelTeam | None = None
        self.platform = None
        self.expiring_at = None
        self.errors = []
        self.data = None
        self.settings = {}
        self._data_validated = False

        if "channel_team" in kwargs:
            self._init_encoding(**kwargs)
        elif "data" in kwargs:
            self._init_decoding(**kwargs)
        else:
            raise KeyError("'channel_team' or 'data' is required at instance creation.")

    def _init_encoding(self, **kwargs):
        self.channel_team = kwargs.get("channel_team")
        self.platform = kwargs.get("platform")
        self.expiring_at = kwargs.get("expiring_at")

    def _init_decoding(self, **kwargs):
        self.data = kwargs.get("data")

    def enc_and_hash_are_valid(self, raise_exception=False):
        self.errors = []
        try:
            self._parse_channel_team()
        except Exception as e:
            logging.getLogger("django").exception(e)
            self.errors.append(MALFORMED_REQUEST)
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        return len(self.errors) == 0

    def validate_data(self, raise_exception=False):
        self.errors = []
        try:
            self._parse_channel_team()
            self._parse_expiring_at()
            # self.__parse_platform()
            self._parse_content()
        except Exception as e:
            logging.getLogger("django").exception(e)
            self.errors.append(MALFORMED_REQUEST)
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        self._data_validated = True
        return len(self.errors) == 0

    def _parse_channel_team(self):
        try:
            encrypted_channel_team_id = self.data.get(self.key_channel_team)
            self.channel_team = ChannelTeam.objects.get(id=self.decrypt(encrypted_channel_team_id))
            validation_hash = self.data.get(self.key_validation_hash)
            if self.channel_team is None or validation_hash != self.hash(self.channel_team.id):
                self.errors.append(MALFORMED_TEAM)
        except (KeyError, ChannelTeam.DoesNotExist, cryptography.fernet.InvalidToken):
            self.errors.append(MALFORMED_TEAM)

    def _parse_expiring_at(self):
        try:
            if not hasattr(self.channel_team, "settings_expiring"):
                self.errors.append(EXPIRED_DATE)
                return
            if timezone.now() >= self.channel_team.settings_expiring.expires:
                self.errors.append(EXPIRED_DATE)
                return
        except (KeyError, ParserError, ChannelTeam.DoesNotExist):
            self.errors.append(MALFORMED_DATE)

    def _parse_platform(self):
        try:
            platform = self.data.get(self.key_platform)
            if platform not in Platforms.values:
                self.errors.append(MALFORMED_PLATFORM)
        except KeyError:
            self.errors.append(MALFORMED_PLATFORM)

    def _parse_content(self):
        try:
            content = self.data.get(self.key_content)
            self.settings = {x["key"]: x["value"] for x in content}
            if not all(
                k in self.settings
                for k in [
                    "WEEKLY_MATCH_DAY",
                    "LINEUP_NOTIFICATION",
                    "TEAM_SCHEDULING_SUGGESTION",
                    "ENEMY_SCHEDULING_SUGGESTION",
                    "ENEMY_SCHEDULING_SUGGESTION_POLL",
                    "SCHEDULING_CONFIRMATION",
                    "SCOUTING_WEBSITE",
                    "CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION",
                    "LANGUAGE",
                    "NEW_COMMENTS_OF_UNKNOWN_USERS",
                    "NEW_MATCHES_NOTIFICATION",
                ]
            ):
                self.errors.append(MISSING_CONTENT)
            scouting_website_name = self.settings.pop("SCOUTING_WEBSITE", "").lower()
            self.scouting_website = ScoutingWebsite.objects.get_multi_websites().get(name=scouting_website_name)
            self.language = self.settings.pop("LANGUAGE")
        except (KeyError, ScoutingWebsite.DoesNotExist):
            self.errors.append(MALFORMED_CONTENT)

    @classmethod
    def encrypt(cls, value) -> str:
        if not isinstance(value, str):
            value = str(value)
        value = value.encode(cls._encoding)
        return Fernet(settings.FERNET_KEY).encrypt(value).decode(encoding=cls._encoding)

    @classmethod
    def decrypt(cls, value) -> str:
        value = value.encode(cls._encoding)
        return Fernet(settings.FERNET_KEY).decrypt(value).decode(encoding=cls._encoding)

    def generate_expiring_link(
        self,
        platform,
        expiring_at: datetime | None = None,
    ) -> str:
        if expiring_at is None:
            expiring_at = timezone.now() + timedelta(minutes=settings.TEMP_LINK_TIMEOUT_MINUTES)

        SettingsExpiring.objects.filter(channel_team=self.channel_team).delete()
        SettingsExpiring.objects.create(expires=expiring_at, channel_team=self.channel_team)
        url = settings.SITE_ID + "/settings/?"
        qps = {
            self.key_channel_team: self.encrypt(self.channel_team.id),
            self.key_validation_hash: self.hash(self.channel_team.id),
            self.key_platform: platform,
        }
        url += parse.urlencode(qps, doseq=False)
        return url

    def save(self):
        if not self._data_validated:
            raise Exception("call .validate_data() first.")
        for key, value in self.settings.items():
            setting, _ = self.channel_team.settings.update_or_create(
                attr_name=key,
                defaults={
                    "attr_value": value,
                },
            )

        self.channel_team.channel.scouting_website = self.scouting_website
        self.channel_team.channel.language = self.language
        self.channel_team.channel.save()

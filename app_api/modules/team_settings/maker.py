import urllib
from datetime import timedelta
from urllib.parse import urlparse

import cryptography
from cryptography.fernet import Fernet
from dateutil.parser import ParserError
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app_prime_league.models import Team, SettingsExpiring, ScoutingWebsite
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

    key_team = "enc"
    key_validation_hash = "hash"
    key_expiring_at = "expiring_at"
    key_platform = "platform"
    key_content = "settings"

    def __init__(self, **kwargs):
        self.team = None
        self.platform = None
        self.expiring_at = None
        self.errors = []
        self.data = None
        self.settings = {}
        self.__data_validated = False

        if "team" in kwargs:
            self.__init_encoding(**kwargs)
            return
        if "data" in kwargs:
            self.__init_decoding(**kwargs)
            return
        raise KeyError("'team' or 'data' is required at instance creation.")

    def __init_encoding(self, **kwargs):
        self.team = kwargs.get("team")
        self.platform = kwargs.get("platform")
        self.expiring_at = kwargs.get("expiring_at")

    def __init_decoding(self, **kwargs):
        self.data = kwargs.get("data")

    def enc_and_hash_are_valid(self, raise_exception=False):
        self.errors = []
        try:
            self.__parse_team()
        except Exception:
            self.errors.append(MALFORMED_REQUEST)
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        return len(self.errors) == 0

    def validate_data(self, raise_exception=False):
        self.errors = []
        try:
            self.__parse_team()
            self.__parse_expiring_at()
            # self.__parse_platform()
            self.__parse_content()
        except Exception:
            self.errors.append(MALFORMED_REQUEST)
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        self.__data_validated = True
        return len(self.errors) == 0

    def __parse_team(self):
        try:
            encrypted_team_id = self.data.get(self.key_team)
            self.team = Team.objects.get(id=self.decrypt(encrypted_team_id))
            validation_hash = self.data.get(self.key_validation_hash)
            if self.team is None or validation_hash != self.hash(self.team.id):
                self.errors.append(MALFORMED_TEAM)
        except (KeyError, Team.DoesNotExist, cryptography.fernet.InvalidToken):
            self.errors.append(MALFORMED_TEAM)

    def __parse_expiring_at(self):
        try:
            if not hasattr(self.team, "settings_expiring"):
                self.errors.append(EXPIRED_DATE)
                return
            if timezone.now() >= self.team.settings_expiring.expires:
                self.errors.append(EXPIRED_DATE)
                return
        except (KeyError, ParserError, Team.DoesNotExist):
            self.errors.append(MALFORMED_DATE)

    def __parse_platform(self):
        try:
            platform = self.data.get(self.key_platform)
            if platform not in ["discord", "telegram"]:
                self.errors.append(MALFORMED_PLATFORM)
        except (KeyError,):
            self.errors.append(MALFORMED_PLATFORM)

    def __parse_content(self):
        try:
            content = self.data.get(self.key_content)
            self.settings = {x["key"]: x["value"] for x in content}
            if not all(k in self.settings for k in [
                "WEEKLY_MATCH_DAY",
                "LINEUP_NOTIFICATION",
                "TEAM_SCHEDULING_SUGGESTION",
                "ENEMY_SCHEDULING_SUGGESTION",
                "SCHEDULING_CONFIRMATION",
                "SCOUTING_WEBSITE",
                "NEW_COMMENTS_OF_UNKNOWN_PERSONS",
            ]):
                self.errors.append(MISSING_CONTENT)
            scouting_website_name = self.settings.pop("SCOUTING_WEBSITE")
            if scouting_website_name != settings.DEFAULT_SCOUTING_NAME:
                scouting_website_name = scouting_website_name.lower()
                self.scouting_website = ScoutingWebsite.objects.get_multi_websites().get(
                    name=scouting_website_name)
            else:
                self.scouting_website = scouting_website_name
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

    def generate_expiring_link(self, platform, expiring_at=None, ) -> str:
        if expiring_at is None:
            expiring_at = timezone.now() + timedelta(minutes=settings.TEMP_LINK_TIMEOUT_MINUTES)

        SettingsExpiring.objects.filter(team=self.team).delete()
        SettingsExpiring.objects.create(expires=expiring_at, team=self.team)
        url = settings.SITE_ID + "/settings/?"
        qps = {
            self.key_team: self.encrypt(self.team.id),
            self.key_validation_hash: self.hash(self.team.id),
            self.key_platform: platform
        }
        url += urllib.parse.urlencode(qps, doseq=False, )
        return url

    def save(self):
        if not self.__data_validated:
            raise Exception("call .validate_data first.")
        for key, value in self.settings.items():
            setting, _ = self.team.setting_set.get_or_create(attr_name=key, defaults={
                "attr_value": value,
            })
            setting.attr_value = value
            setting.save()

        if self.scouting_website != settings.DEFAULT_SCOUTING_NAME:
            self.team.scouting_website = self.scouting_website
            self.team.save()

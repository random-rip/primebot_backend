import hashlib
import urllib
from datetime import datetime, timedelta
from urllib.parse import urlparse

import cryptography
from cryptography.fernet import Fernet
from dateutil.parser import ParserError
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app_prime_league.models import Team, SettingsExpiring

MALFORMED_REQUEST = "invalid_request"
MALFORMED_TEAM = "invalid_team"
MALFORMED_DATE = "invalid_date"
MALFORMED_PLATFORM = "invalid_platform"
MALFORMED_CONTENT = "invalid_content"
EXPIRED_DATE = "url_expired"


class SettingsMaker:
    """
    Class to handle the whole cryptography logic, encoding and decoding data, validating data and creating temporary
    links.
    """
    __hash_func = hashlib.sha256
    __encoder = "utf-8"

    qp_team = "enc"
    qp_validation_hash = "hash"
    qp_expiring_at = "expiring_at"
    qp_platform = "platform"

    def __init__(self, **kwargs):
        self.team = None
        self.platform = None
        self.expiring_at = None
        self.errors = []
        self.data = None

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
            raise
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        return len(self.errors) == 0

    def data_is_valid(self, raise_exception=False):
        self.errors = []
        try:
            self.__parse_team()
            self.__parse_expiring_at()
            # self.__parse_platform()
            self.__parse_content()
        except Exception:
            self.errors.append(MALFORMED_REQUEST)
            raise
        if raise_exception and len(self.errors) > 0:
            raise ValidationError({"errors": self.errors})
        return len(self.errors) == 0

    def __parse_team(self):
        try:
            encrypted_team_id = self.data.get(self.qp_team)
            self.team = Team.objects.get(id=self.decrypt(encrypted_team_id))
            validation_hash = self.data.get(self.qp_validation_hash)
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
            platform = self.data.get(self.qp_platform)
            if platform not in ["discord", "telegram"]:
                self.errors.append(MALFORMED_PLATFORM)
        except (KeyError,):
            self.errors.append(MALFORMED_PLATFORM)

    def __parse_content(self):
        try:
            pass
        except (KeyError,):
            self.errors.append(MALFORMED_CONTENT)

    @classmethod
    def encrypt(cls, value) -> str:
        if not isinstance(value, str):
            value = str(value)
        value = value.encode(cls.__encoder)
        return Fernet(settings.FERNET_KEY).encrypt(value).decode(encoding=cls.__encoder)

    @classmethod
    def decrypt(cls, value) -> str:
        value = value.encode(cls.__encoder)
        return Fernet(settings.FERNET_KEY).decrypt(value).decode(encoding=cls.__encoder)

    @classmethod
    def hash(cls, value) -> str:
        if not isinstance(value, str):
            value = str(value)
        value = value.encode(cls.__encoder)
        return cls.__hash_func(value).hexdigest()

    def generate_expiring_link(self, platform, expiring_at=None, ) -> str:
        if expiring_at is None:
            expiring_at = timezone.now() + timedelta(hours=1)

        SettingsExpiring.objects.filter(team=self.team).delete()
        SettingsExpiring.objects.create(expires=expiring_at, team=self.team)
        url = settings.PRIMEBOT_BASE_URL + "/api/settings/?"
        qps = {
            self.qp_team: self.encrypt(self.team.id),
            self.qp_validation_hash: self.hash(self.team.id),
            self.qp_expiring_at: expiring_at.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            self.qp_platform: platform
        }
        url += urllib.parse.urlencode(qps, doseq=False, )
        return url

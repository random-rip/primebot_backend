import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from cryptography.fernet import Fernet
from dateutil.parser import ParserError
from django.conf import settings
from django.utils import timezone

from app_prime_league.models import Team, SettingsExpiring

MalformedRequest = (0, "Request kaputt",)
MalformedTeam = (1, "Team kaputt",)
MalformedExpiringAt = (2, "expiring kaputt",)
MalformedPlatform = (3, "Platform kaputt",)
MalformedContent = (4, "Content kaputt",)
ExpiredExpiringAt = (5, "expired",)


class SettingsMaker:
    """
    WIP Classname. Class to create temporary links.
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

        if "team" in kwargs:
            self.__init_encoding(**kwargs)
            return
        if "data" in kwargs:
            self.__init_decoding(**kwargs)
            return
        raise KeyError("'team' xor 'link' is required at instance creation.")

    def __init_encoding(self, **kwargs):
        self.team = kwargs.get("team")
        self.platform = kwargs.get("platform")
        self.expiring_at = kwargs.get("expiring_at")

    def __init_decoding(self, **kwargs):
        self.link = kwargs.get("link")

    def link_is_valid(self):
        parsed_url = urlparse(self.link)
        values = parse_qs(parsed_url.query)
        self.errors = []
        try:
            self.__parse_team(values)
            self.__parse_expiring_at(values)
            self.__parse_platform(values)
            self.__parse_content(values)
        except Exception:
            self.errors.append(MalformedRequest)
        return len(self.errors) == 0

    def __parse_team(self, values):
        try:
            encrypted_team_id = values[self.qp_team][0]
            self.team = Team.objects.get(id=self.decrypt(encrypted_team_id))
            validation_hash = values[self.qp_validation_hash][0]
            if self.team is None or validation_hash != self.hash(self.team.id):
                self.errors.append(MalformedTeam)
        except (KeyError, Team.DoesNotExist):
            self.errors.append(MalformedTeam)

    def __parse_expiring_at(self, values):
        try:
            expiring_at = datetime.strptime(values[self.qp_expiring_at][0], '%Y-%m-%dT%H:%M:%S.%f')
            expiring_at = expiring_at.replace(tzinfo=timezone.utc)
            if not hasattr(self.team, "settings_expiring"):
                self.errors.append(ExpiredExpiringAt)
                return
            if expiring_at != self.team.settings_expiring.expires:
                self.errors.append(MalformedExpiringAt)
                return
            if timezone.now() >= expiring_at:
                self.errors.append(ExpiredExpiringAt)
                return
        except (KeyError, ParserError, Team.DoesNotExist):
            self.errors.append(MalformedExpiringAt)

    def __parse_platform(self, values):
        try:
            platform = values[self.qp_platform][0]
            if platform not in ["discord", "telegram"]:
                self.errors.append(MalformedPlatform)
        except (KeyError,):
            self.errors.append(MalformedPlatform)

    def __parse_content(self, values):
        try:
            pass
        except (KeyError,):
            self.errors.append(MalformedContent)

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
        for key, value in qps.items():
            url += f"&{key}={value}"
        return url

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from app_prime_league.models.scouting_website import ScoutingWebsite


class ChannelTeam(models.Model):
    """Through model to connect channels and teams"""

    channel = models.ForeignKey("Channel", on_delete=models.CASCADE, related_name="channel_teams")
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="channel_teams")
    discord_role_id = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["channel", "team"], name="unique_channel_team")]
        verbose_name = _("Channel-Team Relation")
        verbose_name_plural = _("Channel-Team Relations")

    def __str__(self):
        return f"Channel-Team-Relation ({self.channel_id} - {self.team_id})"

    def value_of_setting(self, setting: str, default=True):
        return self.settings_dict().get(setting, default)

    def settings_dict(self):
        return dict(self.settings.values_list("attr_name", "attr_value"))


class Languages(models.TextChoices):
    GERMAN = "de", _("german")
    ENGLISH = "en", _("english")


class Platforms(models.TextChoices):
    DISCORD = "discord", _("Discord")
    TELEGRAM = "telegram", _("Telegram")


class ChannelManager(models.Manager):

    def get_channels_by_ids(self, ids):
        return self.filter(
            Q(platform=Platforms.DISCORD, discord_channel_id__in=ids)
            | Q(platform=Platforms.TELEGRAM, telegram_id__in=ids)
        )


class Channel(models.Model):
    """A channel represents a Text-Chat for example a Text-Channel in Discord or a Group-Chat in Telegram"""

    platform = models.CharField(max_length=10, choices=Platforms.choices, default=Platforms.DISCORD)

    telegram_id = models.CharField(max_length=50, null=True, unique=True, blank=True)
    name = models.TextField(default="", blank=True)

    discord_guild_id = models.CharField(max_length=50, null=True, blank=True)
    discord_webhook_id = models.CharField(max_length=50, null=True, unique=True, blank=True)
    discord_webhook_token = models.CharField(max_length=100, null=True, blank=True)
    discord_channel_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    teams = models.ManyToManyField("Team", through=ChannelTeam, related_name="channels")

    scouting_website = models.ForeignKey(
        "app_prime_league.ScoutingWebsite",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    language = models.CharField(max_length=2, choices=Languages.choices, default=Languages.GERMAN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ChannelManager()

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")

    def __str__(self):
        return f"{self.platform} - {self.id}"

    def get_real_channel_id(self):
        return self.discord_channel_id or self.telegram_id

    def get_scouting_website(self):
        return self.scouting_website or ScoutingWebsite.default()

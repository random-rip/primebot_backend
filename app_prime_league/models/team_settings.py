from django.db import models

from .team_and_match import Team


class Setting(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=50)
    attr_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings"
        unique_together = [("team", "attr_name"), ]
        verbose_name = "Teameinstellung"
        verbose_name_plural = "Teameinstellungen"


class SettingsExpiring(models.Model):
    expires = models.DateTimeField()
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="settings_expiring")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings_expiring"
        verbose_name = "Einstellungslink"
        verbose_name_plural = "Einstellungslinks"

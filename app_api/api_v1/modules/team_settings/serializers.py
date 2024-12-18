from django.conf import settings
from rest_framework import serializers

from app_prime_league.models import Team


class SingleSettingSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()

    create = None
    update = None

    def to_representation(self, instance):
        if type(instance["value"]) is bool:
            self.fields["value"] = serializers.BooleanField()
        else:
            self.fields["value"] = serializers.CharField()
        ret = super().to_representation(instance)
        return ret


class SettingsTeamSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    platforms = serializers.ListField(child=serializers.CharField(), allow_null=True)
    settings = serializers.ListField(child=SingleSettingSerializer(), allow_null=True)
    expiring_at = serializers.DateTimeField(allow_null=True)
    logo_url = serializers.URLField(allow_null=True)

    create = None
    update = None


def team_to_serializer_data(team: Team):
    platforms = []
    if team.discord_channel_id is not None:
        platforms.append("discord")
    if team.telegram_id is not None:
        platforms.append("telegram")

    team_settings_keys = [
        "WEEKLY_MATCH_DAY",
        "LINEUP_NOTIFICATION",
        "ENEMY_SCHEDULING_SUGGESTION",
        "ENEMY_SCHEDULING_SUGGESTION_POLL",
        "TEAM_SCHEDULING_SUGGESTION",
        "SCHEDULING_CONFIRMATION",
        "NEW_COMMENTS_OF_UNKNOWN_USERS",
        "NEW_MATCHES_NOTIFICATION",
    ]
    team_settings = [
        {
            "key": key,
            "value": team.value_of_setting(key),
        }
        for key in team_settings_keys
    ]
    team_settings += [
        {
            "key": "CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION",
            "value": team.value_of_setting("CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION", default=False),
            # Defaults to false instead of true, because its a beta feature
        },
        {
            "key": "SCOUTING_WEBSITE",
            "value": team.scouting_website.name if team.scouting_website else settings.DEFAULT_SCOUTING_NAME,
        },
        {
            "key": "LANGUAGE",
            "value": team.language,
        },
    ]
    serializer = SettingsTeamSerializer(
        {
            "team_id": team.id,
            "team_name": team.name,
            "platforms": platforms,
            "settings": team_settings,
            "expiring_at": team.settings_expiring.expires,
            "logo_url": team.logo_url,
        }
    )
    return serializer.data

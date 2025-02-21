from django.conf import settings
from rest_framework import serializers

from app_prime_league.models import ChannelTeam


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
    channel_name = serializers.CharField(default=None)
    platforms = serializers.ListField(child=serializers.CharField(), allow_null=True)
    settings = serializers.ListField(child=SingleSettingSerializer(), allow_null=True)
    expiring_at = serializers.DateTimeField(allow_null=True)
    logo_url = serializers.URLField(allow_null=True)

    create = None
    update = None


def create_settings_json(channel_team: ChannelTeam):
    channel = channel_team.channel
    team = channel_team.team

    team_settings_keys = [
        "WEEKLY_MATCH_DAY",
        "LINEUP_NOTIFICATION",
        "ENEMY_SCHEDULING_SUGGESTION",
        "ENEMY_SCHEDULING_SUGGESTION_POLL",
        "TEAM_SCHEDULING_SUGGESTION",
        "SCHEDULING_CONFIRMATION",
        "NEW_COMMENTS_OF_UNKNOWN_USERS",
        "NEW_MATCHES_NOTIFICATION",
        "MATCH_RESULT",
    ]
    _settings = [
        {
            "key": key,
            "value": channel_team.value_of_setting(key),
        }
        for key in team_settings_keys
    ]
    _settings += [
        {
            "key": "CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION",
            "value": channel_team.value_of_setting("CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION", default=False),
            # Defaults to false instead of true, because its a beta feature
        },
        {
            "key": "SCOUTING_WEBSITE",
            "value": channel.scouting_website.name if channel.scouting_website else settings.DEFAULT_SCOUTING_NAME,
        },
        {
            "key": "LANGUAGE",
            "value": channel.language,
        },
    ]
    serializer = SettingsTeamSerializer(
        {
            "team_id": team.id,
            "team_name": team.name,
            "platforms": [channel.platform],
            "settings": _settings,
            "expiring_at": channel_team.settings_expiring.expires,
            "logo_url": team.logo_url,
            "channel_name": channel.name or channel.get_real_channel_id(),
        }
    )
    return serializer.data

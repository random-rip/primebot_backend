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

    create = None
    update = None


def team_to_serializer_data(team: Team):
    platforms = []
    if team.discord_channel_id is not None:
        platforms.append("discord")
    if team.telegram_id is not None:
        platforms.append("telegram")

    team_settings = [
        {
            "key": "WEEKLY_OP_LINK",
            "value": team.value_of_setting("WEEKLY_OP_LINK")
        },
        {
            "key": "PIN_WEEKLY_OP_LINK",
            "value": team.value_of_setting("PIN_WEEKLY_OP_LINK"),
        },
        {
            "key": "LINEUP_OP_LINK",
            "value": team.value_of_setting("LINEUP_OP_LINK"),
        },
        {
            "key": "SCHEDULING_SUGGESTION",
            "value": team.value_of_setting("SCHEDULING_SUGGESTION"),
        },
        {
            "key": "SCHEDULING_CONFIRMATION",
            "value": team.value_of_setting("SCHEDULING_CONFIRMATION"),
        },
        {
            "key": "SCOUTING_WEBSITE",
            "value": team.scouting_website.name if team.scouting_website else settings.DEFAULT_SCOUTING_NAME,
        },

    ]
    serializer = SettingsTeamSerializer({
        "team_id": team.id,
        "team_name": team.name,
        "platforms": platforms,
        "settings": team_settings,
    })
    return serializer.data

from rest_framework import serializers

from app_api.common.serializers import PlayerSerializer
from app_prime_league.models import Match, Team


class MinimalTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'team_tag',
            "prime_league_link",
            'logo_url',
        ]


class MatchSerializer(serializers.ModelSerializer):
    team = MinimalTeamSerializer()
    enemy_team = MinimalTeamSerializer()

    class Meta:
        model = Match
        fields = [
            'id',
            'match_id',
            "prime_league_link",
            'result',
            'team',
            'enemy_team',
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    team = MinimalTeamSerializer()
    enemy_team = MinimalTeamSerializer()
    team_lineup = PlayerSerializer(many=True)
    enemy_lineup = PlayerSerializer(many=True)

    class Meta:
        model = Match
        fields = [
            'id',
            'match_id',
            'begin',
            'result',
            "prime_league_link",
            'match_day',
            'match_type',
            'team_lineup',
            'enemy_lineup',
            'team',
            'enemy_team',
        ]

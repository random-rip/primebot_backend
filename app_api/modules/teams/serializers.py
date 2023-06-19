from rest_framework import serializers

from app_api.common.serializers import PlayerSerializer
from app_prime_league.models import Match, Team


class EnemyTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'id',
            "name",
            'team_tag',
            "updated_at",
        ]


class TeamSerializer(serializers.ModelSerializer):
    matches_count = serializers.IntegerField(source="_matches_count")

    class Meta:
        model = Team
        fields = [
            'id',
            "name",
            'team_tag',
            'matches_count',
            "updated_at",
        ]


class MatchForTeamDetailsSerializer(serializers.ModelSerializer):
    enemy_team = EnemyTeamSerializer()
    team_lineup = PlayerSerializer(many=True)
    enemy_lineup = PlayerSerializer(many=True)

    class Meta:
        model = Match
        fields = [
            "match_id",
            "prime_league_link",
            'begin',
            'result',
            'match_day',
            'match_type',
            "updated_at",
            "enemy_team",
            'team_lineup',
            'enemy_lineup',
        ]


class TeamDetailSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, source="player_set")
    matches = MatchForTeamDetailsSerializer(many=True, source="matches_against")

    class Meta:
        model = Team
        fields = [
            'id',
            'team_tag',
            'name',
            "prime_league_link",
            'division',
            'updated_at',
            'logo_url',
            'players',
            'matches',
        ]

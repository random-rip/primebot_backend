from rest_framework import serializers

from app_prime_league.models import Team, Match, Player


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'id',
            'team_tag',
            'division',
        ]


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'id',
            'summoner_name',
            'name',
            'is_leader',
            'created_at',
            'updated_at',
        ]


class MatchIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id',
        ]


class TeamDetailSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, source="player_set")
    matches_against = MatchIdSerializer(many=True)

    class Meta:
        model = Team
        fields = [
            'id',
            'team_tag',
            'name',
            'division',
            'players',
            'created_at',
            'updated_at',
            'logo_url',
            'matches_against',
        ]


class MatchSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    enemy_team = TeamSerializer()

    class Meta:
        model = Match
        fields = [
            'id',
            'match_id',
            'team',
            'enemy_team',
            'result',
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    enemy_team = TeamSerializer()

    class Meta:
        model = Match
        fields = [
            'id',
            'match_id',
            'team',
            'enemy_team',
            'result',
            'match_day',
            'match_type',
            'team_lineup',
            'enemy_lineup',
            'begin',
        ]

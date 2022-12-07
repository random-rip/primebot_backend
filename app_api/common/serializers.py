from rest_framework import serializers

from app_prime_league.models import Team, Match, Player


class TeamSerializer(serializers.ModelSerializer):
    matches_count = serializers.IntegerField(source="matches_against.count")

    class Meta:
        model = Team
        fields = [
            'id',
            "name",
            'team_tag',
            'matches_count',
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


class TeamDetailSerializer(serializers.ModelSerializer):
    class MatchSerializer(serializers.ModelSerializer):
        enemy_team_name = serializers.CharField(source="enemy_team.name")

        class Meta:
            model = Match
            fields = [
                'id',
                "match_id",
                "enemy_team_id",
                "enemy_team_name",
            ]

    players = PlayerSerializer(many=True, source="player_set")
    matches_against = MatchSerializer(many=True)

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
    team_lineup = PlayerSerializer(many=True)
    enemy_lineup = PlayerSerializer(many=True)

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

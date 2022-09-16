from rest_framework import serializers

from app_prime_league.models import Team, Match, Player


class TeamSerializer(serializers.ModelSerializer):  # confirmed
    class Meta:
        model = Team
        fields = ['id',
                  'team_tag',
                  'division',
                  # 'id',
                  # 'team_tag',
                  # 'name',
                  # 'division',
                  # 'player_set',
                  # 'created_at',
                  # 'updated_at',
                  # 'logo_url',
                  # 'matches_against',

                  # 'telegram_id',
                  # 'discord_webhook_id',
                  # 'discord_webhook_token',
                  # 'discord_channel_id',
                  # 'discord_role_id',
                  # 'language'
                  ]


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['summoner_name',
                  'name',
                  'is_leader',

                  # 'id',
                  # 'matches',
                  # 'matches_as_enemy',
                  # 'created_at',
                  # 'updated_at',
                  # 'team',
                  # 'team_id',
                  ]


class MatchIdSerializer(serializers.ModelSerializer):  # confirmed
    class Meta:
        model = Match
        fields = ['id',
                  ]


class TeamDetailSerializer(serializers.ModelSerializer):  # confirmed
    player_set = PlayerSerializer(many=True)
    matches_against = MatchIdSerializer(many=True)

    class Meta:
        model = Team
        fields = [
            'id',
            'team_tag',
            'name',
            'division',
            'player_set',
            'created_at',
            'updated_at',
            'logo_url',
            'matches_against',

            # 'telegram_id',
            # 'discord_webhook_id',
            # 'discord_webhook_token',
            # 'discord_channel_id',
            # 'discord_role_id',
            # 'language'
        ]


class MatchSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    enemy_team = TeamSerializer()

    class Meta:
        model = Match
        fields = ['id',
                  'match_id',
                  'team',
                  'enemy_team',
                  'result',
                  # 'match_day',
                  # 'match_type',
                  # 'team_lineup',
                  # 'enemy_lineup',
                  # 'comment_set',
                  # 'created_at',
                  # 'begin',
                  # 'team_id',
                  # 'enemy_team_id',

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
            # 'team_lineup',
            # 'enemy_lineup',
            # 'comment_set',
            # 'created_at',
            # 'begin',
            # 'team_id',
            # 'enemy_team_id',

        ]

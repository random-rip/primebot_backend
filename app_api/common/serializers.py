from rest_framework import serializers

from app_prime_league.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'id',
            'summoner_name',
            'name',
            'is_leader',
            'updated_at',
        ]

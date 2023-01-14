from django.db import models

from app_prime_league.model_manager import PlayerManager


class Player(models.Model):
    name = models.CharField(max_length=50)
    team = models.ForeignKey("app_prime_league.Team", on_delete=models.CASCADE, null=True)
    summoner_name = models.CharField(max_length=30, null=True)
    is_leader = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    class Meta:
        db_table = "players"
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"Player {self.name}"

from django.db import models

from app_prime_league.model_manager import ChampionManager


class Champion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    banned = models.BooleanField()
    banned_until = models.DateField(null=True, blank=True)
    banned_until_patch = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ChampionManager()

    class Meta:
        db_table = "champions"
        verbose_name = "Champion"
        verbose_name_plural = "Champions"

    def __str__(self):
        return self.name

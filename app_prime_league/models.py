from django.db import models


# Create your models here.

class TeamManager(models.Manager):

    def get_watched_teams(self):
        return self.model.objects.filter(watch=True)


class Team(models.Model):
    name = models.CharField(max_length=50, null=True)
    group_link = models.CharField(max_length=300, null=True)
    watch = models.BooleanField(default=True)

    objects = TeamManager()

    class Meta:
        db_table = "teams"

    def __repr__(self):
        return f"{self.id} - {self.name}"


class Player(models.Model):
    name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "players"

    def __repr__(self):
        return f"{self.name}"


class Game(models.Model):
    game_id = models.BigIntegerField(primary_key=True)

    game_day = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_as_enemy_team")

    class Meta:
        db_table = "games"

    def __repr__(self):
        return f"{self.game_id}"


class Log(models.Model):
    timestamp = models.DateTimeField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    action = models.CharField(max_length=30)
    details = models.TextField(null=True)

    class Meta:
        db_table = "logs"

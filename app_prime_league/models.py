from django.db import models

# Create your models here.
from parsing.regex_operations import MatchHTMLParser


class TeamManager(models.Manager):

    def get_watched_teams(self):
        return self.model.objects.filter(telegram_channel_id__isnull=False)


class GameManager(models.Manager):

    def get_uncompleted_games(self):
        return self.model.objects.filter(game_closed=False)

    def get_latest_suggestion_log(self):
        return self.model.objects.log_set.filter(action="suggestion").order("-timestamp").first()


class Team(models.Model):
    name = models.CharField(max_length=50, null=True)
    group_link = models.CharField(max_length=300, null=True)
    telegram_channel_id = models.CharField(max_length=50, null=True)

    objects = TeamManager()

    class Meta:
        db_table = "teams"

    def __repr__(self):
        return f"{self.id} - {self.name}"


class Player(models.Model):
    name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    is_leader = models.BooleanField(default=False)

    class Meta:
        db_table = "players"

    def __repr__(self):
        return f"{self.name}"


class GameMetaData:

    def __init__(self):
        self.game_id = None
        self.game_day = None
        self.team = None
        self.enemy_team = None
        self.enemy_lineup = None
        self.game_closed = None
        self.latest_suggestion = None
        self.suggestion_confirmed = None

    def __repr__(self):
        return f"GameID: {self.game_id}" \
               f"\nGameDay: {self.game_day}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemyTeam: {self.enemy_team}, " \
               f"\nEnemyLineup: {self.enemy_lineup}, " \
               f"\nGameClosed: {self.game_closed}, " \
               f"\nLatestSuggestion: {self.latest_suggestion}, " \
               f"\nSuggestionConfirmed: {self.suggestion_confirmed}, "

    @staticmethod
    def create_game_meta_data_from_website(team: Team, game_id, website, ):
        gmd = GameMetaData()
        parser = MatchHTMLParser(website)

        gmd.game_id = game_id
        gmd.game_day = parser.get_game_day()
        gmd.team = team
        gmd.enemy_team = parser.get_enemy_team_id(team.id)
        gmd.enemy_lineup = parser.get_enemy_lineup()
        gmd.game_closed = parser.get_game_closed()
        gmd.latest_suggestion = parser.get_latest_suggestion()
        gmd.suggestion_confirmed = parser.get_suggestion_confirmed()

        return gmd


class Game(models.Model):
    game_id = models.BigIntegerField(primary_key=True)

    game_day = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_as_enemy_team")

    enemy_lineup = models.ManyToManyField(Player, )
    game_closed = models.BooleanField()

    objects = GameManager()

    class Meta:
        db_table = "games"

    def __repr__(self):
        return f"{self.game_id}"

    def save_or_update(self, gmd: GameMetaData):
        self.game_id = gmd.game_id
        self.game_day = gmd.game_day
        self.team = gmd.team
        enemy_team, _ = Team.objects.get_or_create(id=gmd.enemy_team)
        self.enemy_team = enemy_team
        self.enemy_lineup.clear()
        for i in gmd.enemy_lineup:
            player, _ = Player.objects.get_or_create(name=i)
            self.enemy_lineup.add(player)
        self.game_closed = gmd.game_closed
        self.save()
        # TODO gmd -> Game


class Log(models.Model):
    timestamp = models.DateTimeField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    action = models.CharField(max_length=30)
    details = models.TextField(null=True)

    class Meta:
        db_table = "logs"

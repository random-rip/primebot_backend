from django.db import models

from parsing.regex_operations import MatchHTMLParser
from utils.utils import timestamp_to_datetime


class TeamManager(models.Manager):

    def get_watched_teams(self):
        return self.model.objects.filter(telegram_channel_id__isnull=False)


class GameManager(models.Manager):

    def get_uncompleted_games(self):
        return self.model.objects.filter(game_closed=False)

    def get_game_by_team(self, game_id, team):
        try:
            return self.model.objects.get(game_id=game_id, team=team)
        except self.model.DoesNotExist:
            return None


class Team(models.Model):
    name = models.CharField(max_length=50, null=True)
    short_name = models.CharField(max_length=10, null=True)
    division = models.CharField(max_length=5, null=True)
    telegram_channel_id = models.CharField(max_length=50, null=True)

    objects = TeamManager()

    class Meta:
        db_table = "teams"

    def __repr__(self):
        return f"{self.id} - {self.name}"


class Player(models.Model):
    name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    summoner_name = models.CharField(max_length=30, null=True)
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
        self.game_begin = None

    def __repr__(self):
        return f"GameID: {self.game_id}" \
               f"\nGameDay: {self.game_day}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemyTeam: {self.enemy_team}, " \
               f"\nEnemyLineup: {self.enemy_lineup}, " \
               f"\nGameClosed: {self.game_closed}, " \
               f"\nLatestSuggestion: {self.latest_suggestion}, " \
               f"\nSuggestionConfirmed: {self.game_begin}, "

    @staticmethod
    def create_game_meta_data_from_website(team: Team, game_id, website, ):
        gmd = GameMetaData()
        parser = MatchHTMLParser(website, team)

        gmd.game_id = game_id
        gmd.game_day = parser.get_game_day()
        gmd.team = team
        gmd.enemy_team = parser.get_enemy_team_id()
        gmd.enemy_lineup = parser.get_enemy_lineup()
        gmd.game_closed = parser.get_game_closed()
        gmd.latest_suggestion = parser.get_latest_suggestion()
        gmd.game_begin = parser.get_game_begin()
        return gmd


class Game(models.Model):
    game_id = models.IntegerField()
    game_day = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_as_enemy_team")

    game_begin = models.DateTimeField(null=True)
    enemy_lineup = models.ManyToManyField(Player, )
    game_closed = models.BooleanField()

    objects = GameManager()

    class Meta:
        db_table = "games"
        unique_together = [("game_id", "team")]

    def __repr__(self):
        return f"{self.game_id}"

    def __str__(self):
        return self.__repr__()

    @property
    def get_first_suggested_game_begin(self):
        suggestion = self.suggestion_set.all().order_by("created_at").first()
        return None if suggestion is None else suggestion.game_begin

    def update_from_gmd(self, gmd: GameMetaData):
        self.game_id = gmd.game_id
        self.game_day = gmd.game_day
        self.team = gmd.team
        self.game_begin = gmd.game_begin
        enemy_team, _ = Team.objects.get_or_create(id=gmd.enemy_team)
        self.enemy_team = enemy_team
        self.game_closed = gmd.game_closed
        self.save()
        if gmd.enemy_lineup is not None:
            self.enemy_lineup.clear()
            for id_, name in gmd.enemy_lineup:
                player, _ = Player.objects.get_or_create(id=id_, defaults={
                    "name": name,
                    "team": enemy_team,
                    "summoner_name": None,
                })
                self.enemy_lineup.add(player)

        if gmd.latest_suggestion is not None:
            self.suggestion_set.all().delete()
            for timestamp in gmd.latest_suggestion.details:
                self.suggestion_set.add(Suggestion(game=self, game_begin=timestamp), bulk=False)
        self.save()

    def get_op_link_of_enemies(self, only_lineup=True):
        if only_lineup:
            names = list(self.enemy_lineup.all().values_list("summoner_name", flat=True))
            if len(names) == 0:
                return None
        else:
            names = list(self.enemy_team.player_set.all().values_list("summoner_name", flat=True))
        url = "%2C".join(names)
        return "https://euw.op.gg/multi/query={}".format(url)


class Suggestion(models.Model):
    game_begin = models.DateTimeField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suggestion"

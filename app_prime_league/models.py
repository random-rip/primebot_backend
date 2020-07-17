from django.db import models

from data_crawling.api import crawler
from parsing.parser import TeamHTMLParser, MatchWrapper, TeamWrapper


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


class PlayerManager(models.Manager):

    def create_or_update_players(self, players_list: list, team):
        players = []
        for (id_, name, summoner_name, is_leader,) in players_list:
            player, created = self.model.objects.get_or_create(id=id_, defaults={
                "name": name,
                "team": team,
                "summoner_name": summoner_name,
                "is_leader": False if is_leader is None else is_leader
            })
            if not created:
                player.name = name
                player.team = team
                player.summoner_name = summoner_name
                if is_leader is not None:
                    player.is_leader = is_leader
                player.save()
            players.append(player)
        return players


class Team(models.Model):
    name = models.CharField(max_length=100, null=True)
    team_tag = models.CharField(max_length=100, null=True)
    division = models.CharField(max_length=20, null=True)
    telegram_channel_id = models.CharField(max_length=50, null=True, unique=True)
    logo_url = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

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
        self.latest_confirmation_log = None

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
    def create_game_meta_data_from_website(team: Team, game_id):
        gmd = GameMetaData()
        match_parser = MatchWrapper(game_id, team).parser

        gmd.game_id = game_id
        gmd.game_day = match_parser.get_game_day()
        gmd.team = team
        gmd.enemy_team = {
            "id": match_parser.get_enemy_team_id(),
        }
        gmd.enemy_lineup = match_parser.get_enemy_lineup()
        if gmd.enemy_lineup is not None:
            enemy_tuples = []
            for i in gmd.enemy_lineup:
                enemy_tuples.append((*i,))
            gmd.enemy_lineup = enemy_tuples
        gmd.game_closed = match_parser.get_game_closed()
        gmd.latest_suggestion = match_parser.get_latest_suggestion()
        gmd.game_begin, gmd.latest_confirmation_log = match_parser.get_game_begin()
        return gmd

    def get_enemy_team_data(self):
        if self.enemy_team is None:
            print("GMD is not initialized yet. Aborting...")
            return
        enemy_team_parser = TeamWrapper(team_id=self.enemy_team["id"]).parser
        self.enemy_team["members"] = enemy_team_parser.get_members()
        self.enemy_team["name"] = enemy_team_parser.get_team_name()
        self.enemy_team["tag"] = enemy_team_parser.get_team_tag()
        self.enemy_team["division"] = enemy_team_parser.get_current_division()


class Game(models.Model):
    game_id = models.IntegerField()
    game_day = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_as_enemy_team")

    game_begin = models.DateTimeField(null=True)
    enemy_lineup = models.ManyToManyField(Player, )
    game_closed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        enemy_team, _ = Team.objects.get_or_create(id=gmd.enemy_team["id"])
        self.enemy_team = enemy_team
        self.game_closed = gmd.game_closed
        self.save()

    def update_game_begin(self, gmd):
        self.game_begin = gmd.game_begin
        self.save()

    def update_enemy_team(self, gmd):
        team_dict = gmd.enemy_team
        enemy_team, created = Team.objects.get_or_create(id=self.enemy_team.id, defaults={
            "name": team_dict["name"],
            "team_tag": team_dict["tag"],
            "division": team_dict["division"],
        })
        if not created:
            enemy_team.name = team_dict["name"]
            enemy_team.team_tag = team_dict["tag"]
            enemy_team.division = team_dict["division"]
            enemy_team.save()
        _ = Player.objects.create_or_update_players(team_dict["members"], enemy_team)

    def update_latest_suggestion(self, gmd):
        if gmd.latest_suggestion is not None:
            self.suggestion_set.all().delete()
            for timestamp in gmd.latest_suggestion.details:
                self.suggestion_set.add(Suggestion(game=self, game_begin=timestamp), bulk=False)
        self.save()

    def update_enemy_lineup(self, gmd: GameMetaData):
        if gmd.enemy_lineup is not None:
            self.enemy_lineup.clear()
            players = Player.objects.create_or_update_players(gmd.enemy_lineup, self.enemy_team)
            self.enemy_lineup.add(*players)
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


class Setting(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=50)
    attr_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings"
        unique_together = [("team", "attr_name"), ]

from django.conf import settings
from django.db import models
from django.db.models import Q, F

from modules.processors.match_processor import MatchDataProcessor
from modules.processors.team_processor import TeamDataProcessor


class TeamManager(models.Manager):

    def get_watched_teams(self):
        """
        Gibt alle Teams zurück, die entweder in einer Telegram-Gruppe oder in einem Discord-Channel registriert wurden.
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))

    def get_watched_team_of_current_split(self):
        """
        Gibt alle Teams zurück, die entweder in einer Telegram-Gruppe oder in einem Discord-Channel registriert wurden
        und wo die Division gesetzt wurde!
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False),
                                         division__isnull=False)

    def get_team(self, team_id):
        return self.model.objects.filter(id=team_id).first()

    def get_calibration_teams(self):
        # TODO neues Feld in model
        return self.model.objects.filter(id__in=[116152, 146630, 135572, 153698])
        # return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))


class GameManager(models.Manager):

    def get_uncompleted_games(self):
        return self.model.objects.filter(Q(game_closed=False) | Q(game_closed__isnull=True))

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


class CommentManager(models.Manager):
    pass


class Team(models.Model):
    name = models.CharField(max_length=100, null=True)
    team_tag = models.CharField(max_length=100, null=True)
    division = models.CharField(max_length=20, null=True)
    telegram_id = models.CharField(max_length=50, null=True, unique=True)
    discord_webhook_id = models.CharField(max_length=50, null=True, unique=True)
    discord_webhook_token = models.CharField(max_length=100, null=True)
    discord_channel_id = models.CharField(max_length=50, unique=True, null=True)
    discord_role_id = models.CharField(max_length=50, null=True)
    logo_url = models.CharField(max_length=1000, null=True)
    scouting_website = models.ForeignKey("app_prime_league.ScoutingWebsite", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TeamManager()

    class Meta:
        db_table = "teams"

    def __repr__(self):
        return f"{self.id} - {self.name}"

    def __str__(self):
        return f"Team {self.id} - {self.name}"

    def value_of_setting(self, setting):
        return self.settings_dict().get(setting, True)

    def settings_dict(self):
        return dict(self.setting_set.all().values_list("attr_name", "attr_value"))

    def is_active(self):
        return self.telegram_id or self.discord_channel_id

    def get_next_open_game(self):
        return self.get_open_games_ordered().first()

    def set_telegram_null(self):
        self.telegram_id = None
        self.save(update_fields=["telegram_id"])
        self.soft_delete()

    def set_discord_null(self):
        self.discord_webhook_id = None
        self.discord_channel_id = None
        self.discord_webhook_token = None
        self.discord_role_id = None
        self.save(
            update_fields=["discord_webhook_id", "discord_channel_id", "discord_webhook_token", "discord_role_id"])
        self.soft_delete()

    def soft_delete(self):
        if self.telegram_id is None and self.discord_channel_id is None:
            for game in self.games_against.all():
                game.suggestion_set.all().delete()
                game.enemy_lineup.all().delete()
                game.delete()
            self.setting_set.all().delete()

    def get_scouting_link(self, game, lineup=True):
        """

        :param game:
        :param lineup: If lineup=True and a lineup is available returns just the lineup link
        :return:
        """
        if lineup and game.lineup_available:
            names = list(game.enemy_lineup.all().values_list("summoner_name", flat=True))
        else:
            names = list(game.enemy_team.player_set.all().values_list("summoner_name", flat=True))

        base_url = settings.DEFAULT_SCOUTING_URL if not self.scouting_website else self.scouting_website.base_url
        separator = settings.DEFAULT_SCOUTING_SEP if not self.scouting_website else self.scouting_website.separator
        parameters = f"{separator}".join([x.replace(" ", "") for x in names])
        return base_url.format(parameters)

    def get_open_games_ordered(self):
        return self.games_against.filter(game_closed=False).order_by(F('game_day').desc(nulls_last=True))


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

    def __str__(self):
        return f"Player {self.name}"


class GameMetaData:

    def __init__(self):
        self.game_id = None
        self.game_day = None
        self.team = None
        self.enemy_team = None
        self.enemy_lineup = None
        self.game_closed = None
        self.game_result = None
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
               f"\nGame Result: {self.game_result}" \
               f"\nLatestSuggestion: {self.latest_suggestion}, " \
               f"\nSuggestionConfirmed: {self.game_begin}, "

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def create_game_meta_data_from_website(team: Team, game_id):

        gmd = GameMetaData()
        processor = MatchDataProcessor(game_id, team.id)

        gmd.game_id = game_id
        gmd.game_day = processor.get_game_day()
        gmd.team = team
        gmd.enemy_team = {
            "id": processor.get_enemy_team_id(),
        }
        gmd.enemy_lineup = processor.get_enemy_lineup()
        if gmd.enemy_lineup is not None:
            enemy_tuples = []
            for i in gmd.enemy_lineup:
                enemy_tuples.append((*i,))
            gmd.enemy_lineup = enemy_tuples
        gmd.game_closed = processor.get_game_closed()
        gmd.latest_suggestion = processor.get_latest_suggestion()
        gmd.game_begin, gmd.latest_confirmation_log = processor.get_game_begin()
        gmd.game_result = processor.get_game_result()
        return gmd

    def get_enemy_team_data(self):
        if self.enemy_team is None:
            print("GMD is not initialized yet. Aborting...")
            return
        processor = TeamDataProcessor(team_id=self.enemy_team["id"])
        self.enemy_team["members"] = processor.get_members()
        self.enemy_team["name"] = processor.get_team_name()
        self.enemy_team["tag"] = processor.get_team_tag()
        self.enemy_team["division"] = processor.get_current_division()


class Game(models.Model):
    game_id = models.IntegerField()
    game_day = models.IntegerField(null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="games_as_enemy_team", null=True)

    game_begin = models.DateTimeField(null=True)
    enemy_lineup = models.ManyToManyField(Player, )
    game_closed = models.BooleanField(null=True)
    game_result = models.CharField(max_length=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GameManager()

    class Meta:
        db_table = "games"
        unique_together = [("game_id", "team")]

    def __repr__(self):
        return f"{self.game_id}"

    def __str__(self):
        return f"Game {self.game_id} from {self.team}"

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
        self.game_result = gmd.game_result
        self.save()

    def update_game_begin(self, gmd):
        self.game_begin = gmd.game_begin
        self.save()

    def update_enemy_team(self, gmd):
        team_dict = gmd.enemy_team
        enemy_team, created = Team.objects.get_or_create(id=team_dict["id"], defaults={
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

    @property
    def lineup_available(self):
        return self.enemy_lineup.all().count() > 0


class ScoutingWebsite(models.Model):
    name = models.CharField(max_length=20, unique=True)
    base_url = models.CharField(max_length=200)
    separator = models.CharField(max_length=5, default=settings.DEFAULT_SCOUTING_SEP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scouting_websites"

    def generate_link(self, lineup):
        return self.base_url.format(self.separator.join(lineup))


class Suggestion(models.Model):
    game_begin = models.DateTimeField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suggestions"


class Setting(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=50)
    attr_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings"
        unique_together = [("team", "attr_name"), ]


class Comment(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=50)
    parent = models.ForeignKey('Comment', on_delete=models.CASCADE)
    content = models.CharField(max_length=3000)
    has_more_content = models.BooleanField(default=False)
    author_name = models.CharField(max_length=50)
    author_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    class Meta:
        db_table = "comments"
        unique_together = [("game", "comment_id"), ]


class TeamWatcher(models.Model):
    telegram_id = models.CharField(max_length=50, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "watched_teams"
        unique_together = [("telegram_id", "team"), ]

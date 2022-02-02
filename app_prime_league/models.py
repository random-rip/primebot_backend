from django.conf import settings
from django.db import models
from django.db.models import F
from django.template.defaultfilters import truncatechars

from app_prime_league.model_manager import TeamManager, MatchManager, PlayerManager
from utils.exceptions import GMDNotInitialisedException


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
        verbose_name = "Team"
        verbose_name_plural = "Teams"

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

    def get_next_open_match(self):
        return self.get_open_matches_ordered().first()

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
            for match in self.matches_against.all():
                match.suggestion_set.all().delete()
                match.enemy_lineup.all().delete()
                match.delete()
            self.setting_set.all().delete()

    def get_scouting_link(self, match, lineup=True):
        """
        :param match:
        :param lineup: If lineup=True and a lineup is available returns just the lineup link
        :return:
        """
        if lineup and match.lineup_available:
            names = list(match.enemy_lineup.all().values_list("summoner_name", flat=True))
        else:
            names = list(match.enemy_team.player_set.all().values_list("summoner_name", flat=True))

        base_url = settings.DEFAULT_SCOUTING_URL if not self.scouting_website else self.scouting_website.base_url
        separator = settings.DEFAULT_SCOUTING_SEP if not self.scouting_website else self.scouting_website.separator
        parameters = f"{separator}".join([x.replace(" ", "") for x in names])
        return base_url.format(parameters)

    def get_open_matches_ordered(self):
        return self.matches_against.filter(closed=False).order_by(F('match_day').desc(nulls_last=True))


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
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"Player {self.name}"


class Match(models.Model):
    MATCH_TYPE_CALIBRATION = "calibration"
    MATCH_TYPE_GROUP = "group"  # Pro Div, Kein Divisionssystem
    MATCH_TYPE_LEAGUE = "league"  # Gruppenphase Divisionssystem
    MATCH_TYPE_PLAYOFF = "playoff"

    MATCH_TYPES = (
        (MATCH_TYPE_CALIBRATION, "Kalibrierung"),
        (MATCH_TYPE_GROUP, "Pro Division"),
        (MATCH_TYPE_LEAGUE, "Gruppenphase"),
        (MATCH_TYPE_PLAYOFF, "Playoffs"),
    )

    match_id = models.IntegerField()
    match_day = models.IntegerField(null=True)
    match_type = models.CharField(max_length=15, null=True, choices=MATCH_TYPES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="matches_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="matches_as_enemy_team", null=True)
    team_made_latest_suggestion = models.BooleanField(null=True, blank=True)
    match_begin_confirmed = models.BooleanField(default=False, blank=True)
    begin = models.DateTimeField(null=True)
    enemy_lineup = models.ManyToManyField(Player, )
    closed = models.BooleanField(null=True)
    result = models.CharField(max_length=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MatchManager()

    class Meta:
        db_table = "matches"
        unique_together = [("match_id", "team")]
        verbose_name = "Spiel"
        verbose_name_plural = "Spiele"

    def __repr__(self):
        return f"{self.match_id}"

    def __str__(self):
        return f"Match {self.match_id} from {self.team}"

    @property
    def get_first_suggested_match_begin(self):
        suggestion = self.suggestion_set.all().order_by("created_at").first()
        return None if suggestion is None else suggestion.begin

    def set_enemy_team(self, gmd):
        if self.enemy_team is not None:
            return
        self.enemy_team = Team.objects.get_team(team_id=gmd.enemy_team_id)
        self.save(update_fields=["enemy_team"])

    def update_match_data(self, gmd):
        self.match_id = gmd.match_id
        self.match_day = gmd.match_day
        self.team = gmd.team
        self.begin = gmd.begin
        self.match_begin_confirmed = gmd.match_begin_confirmed
        self.closed = gmd.closed
        self.result = gmd.result
        self.save()

    def update_match_begin(self, gmd):
        self.begin = gmd.begin
        self.match_begin_confirmed = gmd.match_begin_confirmed
        self.save()

    def update_enemy_team(self, gmd):
        if gmd.enemy_team is None:
            raise GMDNotInitialisedException("GMD Enemy Team Data is not initialized yet. Aborting...")
        enemy_team, created = Team.objects.update_or_create(id=gmd.enemy_team_id, defaults=self.enemy_team)
        _ = Player.objects.create_or_update_players(gmd.enemy_team_members, enemy_team)
        self.set_enemy_team(gmd=gmd)

    def update_latest_suggestions(self, gmd):
        if gmd.latest_suggestions is not None:
            self.suggestion_set.all().delete()
            for suggestion in gmd.latest_suggestions:
                self.suggestion_set.add(Suggestion(match=self, begin=suggestion), bulk=False)
        self.team_made_latest_suggestion = gmd.team_made_latest_suggestion
        self.save()

    def update_enemy_lineup(self, md):
        if md.enemy_lineup is not None:
            self.enemy_lineup.clear()
            players = Player.objects.create_or_update_players(md.enemy_lineup, self.enemy_team)
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
        verbose_name = "Scouting-Website"
        verbose_name_plural = "Scouting-Websites"

    def generate_link(self, lineup):
        return self.base_url.format(self.separator.join(lineup))

    def __str__(self):
        return self.name


class Suggestion(models.Model):
    begin = models.DateTimeField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suggestions"
        verbose_name = "Terminvorschlag"
        verbose_name_plural = "Terminvorschläge"


class Setting(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=50)
    attr_value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings"
        unique_together = [("team", "attr_name"), ]
        verbose_name = "Teameinstellung"
        verbose_name_plural = "Teameinstellungen"


class SettingsExpiring(models.Model):
    expires = models.DateTimeField()
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="settings_expiring")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings_expiring"
        verbose_name = "Einstellungslink"
        verbose_name_plural = "Einstellungslinks"


class Comment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=50)
    parent = models.ForeignKey('Comment', on_delete=models.CASCADE)
    content = models.TextField()
    author_name = models.CharField(max_length=50)
    author_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    class Meta:
        db_table = "comments"
        unique_together = [("match", "comment_id"), ]
        verbose_name = "Spielkommentar"
        verbose_name_plural = "Spielkommentare"


class Changelog(models.Model):
    version_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Änderungsprotokoll"
        verbose_name_plural = "Änderungsprotokolle"

    def __str__(self):
        return self.version_number

    @property
    def truncated_description(self):
        return truncatechars(self.description, 100)

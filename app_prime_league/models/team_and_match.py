from django.db import models
from django.db.models import F
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

from app_prime_league.model_manager import MatchManager, PlayerManager
from app_prime_league.model_manager import TeamManager
from .scouting_website import ScoutingWebsite
from .player import Player
from utils.utils import current_match_day


class Team(models.Model):
    class Languages(models.TextChoices):
        GERMAN = "de", _("german")
        ENGLISH = "en", _("english")

    name = models.CharField(max_length=100, null=True, blank=True, )
    team_tag = models.CharField(max_length=100, null=True, blank=True, )
    division = models.CharField(max_length=20, null=True, blank=True, )
    telegram_id = models.CharField(max_length=50, null=True, unique=True, blank=True, )
    discord_webhook_id = models.CharField(max_length=50, null=True, unique=True, blank=True, )
    discord_webhook_token = models.CharField(max_length=100, null=True, blank=True, )
    discord_channel_id = models.CharField(max_length=50, unique=True, null=True, blank=True, )
    discord_role_id = models.CharField(max_length=50, null=True, blank=True, )
    logo_url = models.URLField(max_length=1000, null=True, blank=True, )
    scouting_website = models.ForeignKey("app_prime_league.ScoutingWebsite", on_delete=models.SET_NULL, null=True,
                                         blank=True, )
    language = models.CharField(max_length=2, choices=Languages.choices, default=Languages.GERMAN)
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
        name = self.name or ""
        return f"{self.id}  - {truncatechars(name, 15)}"

    def value_of_setting(self, setting):
        return self.settings_dict().get(setting, True)

    def settings_dict(self):
        return dict(self.setting_set.all().values_list("attr_name", "attr_value"))

    def is_registered(self):
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
            # TODO: team auf standardeinstellungen zurücksetzen (scouting website, sprache)

    def get_scouting_url(self, match: "Match", lineup=True):
        """
        Creates a link of the enemy team of the given match. if `lineup=True` and lineup is available of the
        match, creates the link of the enemy lineup instead.
        :param match: `Match`
        :param lineup: If lineup=True and a lineup is available a link of the lineup is created
        :return: Urlencoded string of team
        """
        if lineup and match.enemy_lineup_available:
            qs = match.enemy_lineup
        else:
            qs = match.get_enemy_team().player_set

        names = list(qs.get_active_players().values_list("summoner_name", flat=True))
        if self.scouting_website:
            website = self.scouting_website
        else:
            website = ScoutingWebsite.default()

        return website.generate_url(names=names)

    def get_open_matches_ordered(self):
        return self.matches_against.filter(closed=False).order_by(F('match_day').asc(nulls_last=True))

    def get_obvious_matches_based_on_stage(self, match_day: int):
        """
        Get ``Match`` queryset, where match_type will be set based on the current stage of the split.
        Args:
            match_day: Match day

        Returns: Matches Queryset based on current stage

        """
        qs_filter = {
            "match_day": match_day,
            "match_type": Match.MATCH_TYPE_LEAGUE,
        }
        week = current_match_day()
        if week <= -1:
            qs_filter["match_type"] = Match.MATCH_TYPE_GROUP
        elif week > 8 and self.matches_against.filter(match_type=Match.MATCH_TYPE_PLAYOFF).exists():
            qs_filter["match_type"] = Match.MATCH_TYPE_PLAYOFF
        return self.matches_against.filter(**qs_filter)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()


class Match(models.Model):
    MATCH_TYPE_GROUP = "group"  # Pro Div und Kalibrierungsphase, Kein Divisionssystem
    MATCH_TYPE_LEAGUE = "league"  # Gruppenphase Divisionssystem
    MATCH_TYPE_PLAYOFF = "playoff"  # Playoffs

    MATCH_TYPES = (
        (MATCH_TYPE_GROUP, "Kalibrierung"),
        (MATCH_TYPE_LEAGUE, "Gruppenphase"),
        (MATCH_TYPE_PLAYOFF, "Playoffs"),
    )

    MATCH_DAY_TIEBREAKER = 99
    MATCH_DAY_PLAYOFF = 0

    match_id = models.IntegerField()
    match_day = models.IntegerField(null=True)
    match_type = models.CharField(max_length=15, null=True, choices=MATCH_TYPES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="matches_against")
    enemy_team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="matches_as_enemy_team", null=True)
    team_made_latest_suggestion = models.BooleanField(null=True, blank=True)
    match_begin_confirmed = models.BooleanField(default=False, blank=True)
    has_side_choice = models.BooleanField()  # Team has side choice in first game
    begin = models.DateTimeField(null=True)
    enemy_lineup = models.ManyToManyField(Player, related_name="matches_as_enemy")
    team_lineup = models.ManyToManyField(Player, related_name="matches")
    closed = models.BooleanField(null=True)
    result = models.CharField(max_length=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MatchManager()

    class Meta:
        db_table = "matches"
        unique_together = [("match_id", "team")]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __repr__(self):
        return f"{self.match_id}"

    def __str__(self):
        return f"{self.match_id} of Team {self.team}"

    def set_enemy_team(self, gmd):
        if self.enemy_team is not None:
            return
        self.enemy_team = Team.objects.get_team(team_id=gmd.enemy_team_id)
        self.save(update_fields=["enemy_team"])

    def update_match_data(self, tmd):
        self.match_id = tmd.match_id
        self.match_day = tmd.match_day
        self.match_type = tmd.match_type
        self.team = tmd.team
        self.begin = tmd.begin
        self.match_begin_confirmed = tmd.match_begin_confirmed
        self.closed = tmd.closed
        self.result = tmd.result
        self.has_side_choice = tmd.has_side_choice
        self.save()

    def update_match_begin(self, gmd):
        self.begin = gmd.begin
        self.match_begin_confirmed = gmd.match_begin_confirmed
        self.save()

    def update_latest_suggestions(self, md):
        if md.latest_suggestions is not None:
            self.suggestion_set.all().delete()
            for suggestion in md.latest_suggestions:
                self.suggestion_set.add(Suggestion(match=self, begin=suggestion), bulk=False)
        self.team_made_latest_suggestion = md.team_made_latest_suggestion
        self.save()

    def update_enemy_lineup(self, md):
        if md.enemy_lineup is not None:
            self.enemy_lineup.clear()
            players = Player.objects.create_or_update_players(md.enemy_lineup, self.enemy_team)
            self.enemy_lineup.add(*players)
            self.save()

    def update_team_lineup(self, tmd):
        if tmd.team_lineup is not None:
            self.team_lineup.clear()
            players = Player.objects.create_or_update_players(tmd.team_lineup, self.team)
            self.team_lineup.add(*players)
            self.save()

    def update_comments(self, tmd):
        for i in tmd.comments:
            Comment.objects.update_or_create(match=self, comment_id=i.comment_id, defaults={**i.comment_as_dict()})

    @property
    def enemy_lineup_available(self):
        return self.enemy_lineup.all().count() > 0

    @property
    def team_lineup_available(self):
        return self.team_lineup.all().count() > 0

    def get_enemy_team(self) -> Team:
        """
        Safe Method to get a `Team` object even if the enemy_team is None.
        Returns: Enemy Team  or dummy Team object

        """
        return self.enemy_team or Team(
            name=_("Deleted Team/TBD"),
            team_tag=_("Deleted Team/TBD"),
        )


class Suggestion(models.Model):
    begin = models.DateTimeField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suggestions"
        verbose_name = "Terminvorschlag"
        verbose_name_plural = "Terminvorschläge"


class Comment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    comment_id = models.IntegerField()
    comment_parent_id = models.IntegerField(verbose_name="Parent ID")
    comment_time = models.DateTimeField()
    content = models.TextField(default="")
    user_id = models.IntegerField()
    comment_edit_user_id = models.IntegerField(verbose_name="Editiert von")
    comment_flag_staff = models.BooleanField(verbose_name="Staff")
    comment_flag_official = models.BooleanField(verbose_name="Official")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlayerManager()

    class Meta:
        db_table = "comments"
        unique_together = [("id", "match"), ]
        verbose_name = "Matchkommentar"
        verbose_name_plural = "Matchkommentare"

    def __str__(self):
        return f"{self.id = }, {self.match = }, {self.comment_id = }"

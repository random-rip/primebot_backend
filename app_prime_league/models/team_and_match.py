from datetime import date, datetime, timedelta
from typing import Union

from django.conf import settings
from django.db import models
from django.db.models import F, Q, QuerySet
from django.db.transaction import atomic
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app_prime_league.model_manager import PlayerManager
from app_prime_league.models.channel import ChannelTeam
from utils.utils import count_weeks

from .player import Player
from .scouting_website import ScoutingWebsite


class SettingIsFalseException(Exception):
    pass


class CurrentSplitTeamManager(models.Manager):
    """Returns all teams of the current split."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(split=Split.objects.get_current_split())


class TeamManager(models.Manager):
    """Returns all teams, no matter which split."""

    @atomic
    def cleanup(self, channel_teams: Union["ChannelTeam", QuerySet]) -> list[str]:
        """
        Deletes the given channel_team relations.
        Soft Deletes multiple teams and their related enemy teams and matches.
        """
        if isinstance(channel_teams, ChannelTeam):
            channel_teams = ChannelTeam.objects.filter(pk=channel_teams.pk)
        elif isinstance(channel_teams, QuerySet):
            pass
        else:
            raise ValueError("channel_teams must be a ChannelTeam instance or a QuerySet.")

        # Primary teams are the teams of the given channel_teams
        primary_teams = Team.objects.filter(channel_teams__in=channel_teams).distinct()

        # Get all enemy teams of the given teams
        enemy_teams = Team.objects.filter(
            matches_as_enemy_team__in=Match.objects.filter(team__in=primary_teams)
        ).distinct()

        # Force evaluation of QuerySet
        primary_teams = list(primary_teams)
        enemy_teams = list(enemy_teams)

        # Delete all channel_teams so that the soft delete of the teams is possible
        channel_teams.delete()

        # Soft delete now all given teams
        ret = set()
        deleted_given_team_names = Team.objects.soft_delete_multiple(primary_teams)
        ret.update(deleted_given_team_names)

        # Soft delete all enemy teams
        deleted_related_team_names = Team.objects.soft_delete_multiple(enemy_teams)
        ret.update(deleted_related_team_names)
        return sorted(ret)

    @atomic
    def soft_delete_multiple(self, teams: list["Team"]) -> list[str]:
        """
        Soft deletes multiple teams.
        That should be called, after a channel_team relation or a channel was deleted.
        """
        deleted_team_names = []
        for team in teams:
            is_deleted = self.soft_delete(team)
            if is_deleted:
                deleted_team_names.append(team.name)
        return deleted_team_names

    @atomic
    def soft_delete(self, team: "Team") -> bool:
        """
        Checks if the team can be deleted and deletes it if possible.
        That should be called, after a channel_team relation or a channel was deleted.
        """
        if team.channels.exists():
            # Some channels have still subscribed to the team
            return False
        # No channels are subscribed to the team, let's check if the team is an enemy team in a match
        if team.matches_as_enemy_team.exists():
            # It's an enemy team in a match, so we cannot delete the team, but we can delete the matches
            team.matches_against.all().delete()
            return False
        # The team is not an enemy team in any match, so we can delete it and the matches
        team.delete()
        return True

    def get_registered_teams(self):
        """
        Gibt alle Teams zurück, die mindestens in einem Channel registriert wurden.
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(channels__gt=0)

    def get_teams_to_update(self):
        """Returns all teams that are registered and all enemy teams of matches that are not closed."""
        teams = self.get_registered_teams()
        matches = Match.objects.filter(
            Q(closed=False) | Q(closed__isnull=True) | Q(closed=True, begin__gte=timezone.now() - timedelta(days=2))
        )
        enemy_teams = Team.objects.filter(matches_as_enemy_team__in=matches)
        return teams.union(enemy_teams)

    def get_team(self, team_id):
        return self.model.objects.filter(id=team_id).first()


class Team(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    team_tag = models.CharField(max_length=100, null=True, blank=True)
    division = models.CharField(max_length=20, null=True, blank=True)
    logo_url = models.URLField(max_length=1000, null=True, blank=True)

    split = models.ForeignKey(
        "app_prime_league.Split", on_delete=models.SET_NULL, null=True, blank=True, related_name="teams"
    )
    """This is the last split the team was registered in, which can be the current split."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TeamManager()
    current_split_objects = CurrentSplitTeamManager()

    class Meta:
        db_table = "teams"
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __repr__(self):
        return f"{self.id} - {self.name}"

    def __str__(self):
        name = self.name or ""
        return f"{self.id}  - {truncatechars(name, 15)}"

    def has_subscriptions(self):
        return self.channels.exists()

    def get_next_open_match(self):
        return self.get_open_matches_ordered().first()

    def get_open_matches_ordered(self):
        return self.matches_against.filter(closed=False).order_by(F('match_day').asc(nulls_last=True))

    def get_obvious_matches_based_on_stage(self, match_day: int | None = None):
        """
        Get ``Match`` queryset, where match_type will be set based on the current stage of the split.
        :param match_day: Filter for optional match_day
        :return: Matches Queryset based on current stage
        """
        qs_filter = {}
        if match_day is not None:
            qs_filter["match_day"] = match_day

        current_split = Split.objects.get_current_split()
        current_stage = current_split.get_current_stage()
        if current_stage == Match.MATCH_TYPE_PLAYOFF:
            if self.matches_against.filter(match_type=Match.MATCH_TYPE_PLAYOFF).exists():
                qs_filter["match_type"] = Match.MATCH_TYPE_PLAYOFF
        else:
            if current_stage is None:
                return self.matches_against.none()
            qs_filter["match_type"] = current_stage
        return self.matches_against.filter(**qs_filter)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    @property
    def prime_league_link(self) -> str:
        return f"{settings.TEAM_URI}{self.id}"


class MatchManager(models.Manager):
    """Returns all matches, no matter which split."""


class CurrentSplitMatchManager(models.Manager):
    """Returns all matches of the current split."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(split=Split.objects.get_current_split())

    def get_matches_to_update(self):
        """
        Gibt alle Matches zurück die nicht `closed` oder `NULL` sind oder deren Spielbeginn weniger als 2 Tage her ist.
        :returns: queryset

        """
        qs = self.model.objects.filter(
            Q(closed=False) | Q(closed__isnull=True) | Q(closed=True, begin__gte=timezone.now() - timedelta(days=2))
        )
        return qs


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
    match_day = models.IntegerField(null=True, blank=True)
    match_type = models.CharField(max_length=15, null=True, choices=MATCH_TYPES, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="matches_against")
    enemy_team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, related_name="matches_as_enemy_team", null=True, blank=True
    )
    team_made_latest_suggestion = models.BooleanField(null=True, blank=True)
    match_begin_confirmed = models.BooleanField(default=False, blank=True)
    datetime_until_auto_confirmation = models.DateTimeField(null=True, blank=True)
    has_side_choice = models.BooleanField(null=True)  # Team has side choice in first game
    begin = models.DateTimeField(null=True, blank=True)
    enemy_lineup = models.ManyToManyField(Player, related_name="matches_as_enemy", blank=True)
    team_lineup = models.ManyToManyField(Player, related_name="matches", blank=True)
    closed = models.BooleanField(null=True)
    result = models.CharField(max_length=5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    split = models.ForeignKey(
        "app_prime_league.Split", on_delete=models.CASCADE, null=True, blank=True, related_name="matches"
    )

    objects = MatchManager()
    current_split_objects = CurrentSplitMatchManager()

    class Meta:
        db_table = "matches"
        constraints = [models.UniqueConstraint(fields=["match_id", "team"], name="unique_match_team")]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __repr__(self):
        return f"{self.match_id}"

    def __str__(self):
        return f"{self.match_id} of Team {self.team}"

    @property
    def enemy_lineup_available(self):
        return self.enemy_lineup.all().count() > 0

    @property
    def team_lineup_available(self):
        return self.team_lineup.all().count() > 0

    def get_enemy_team(self) -> Team:
        """
        Safe Method to get a `Team` object even if the enemy_team is None.
        :return: Enemy Team  or dummy Team object
        """
        return self.enemy_team or Team(
            name=_("Deleted Team/TBD"),
            team_tag=_("Deleted Team/TBD"),
        )

    @property
    def prime_league_link(self) -> str:
        return f"{settings.MATCH_URI}{self.match_id}"

    def get_enemy_scouting_url(self, scouting_website: ScoutingWebsite = None, lineup=True) -> str:
        """
        Creates an url of the enemy team of the given match. if `lineup=True` and lineup is available of the
        enemy team, the url only contains the lineup of the enemy team.
        :param scouting_website: ScoutingWebsite
        :param lineup: Boolean
        :return: String
        """
        scouting_website = scouting_website or ScoutingWebsite.default()
        if lineup and self.enemy_lineup_available:
            qs = self.enemy_lineup
        else:
            enemy_team = self.get_enemy_team()
            qs = Player.objects.none() if enemy_team.id is None else enemy_team.player_set

        names = list(qs.get_active_players().order_by("summoner_name").values_list("summoner_name", flat=True))
        return scouting_website.generate_url(names=names)


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
        unique_together = [
            ("id", "match"),
        ]
        verbose_name = "Matchkommentar"
        verbose_name_plural = "Matchkommentare"

    def __str__(self):
        return f"{self.id=}, {self.match=}, {self.comment_id=}"


class NoCurrentSplitException(Exception):
    pass


class SplitManager(models.Manager):
    def get_current_split(self) -> "Split":
        split = self.model.objects.order_by("-registration_start").first()
        if split is None:
            raise NoCurrentSplitException
        return split


class Split(models.Model):
    name = models.CharField(max_length=20, unique=True)
    registration_start = models.DateField(help_text="Date when registration starts")
    registration_end = models.DateField(help_text="Date when registration ends")
    calibration_stage_start = models.DateField(
        blank=True,
        help_text="Date when calibration stage starts, usually the saturday before the registration ends",
    )
    calibration_stage_end = models.DateField(
        blank=True, help_text="Date when calibration stage ends, usually the sunday before the registration ends"
    )
    group_stage_start = models.DateField(
        blank=True,
        help_text="Date when group stage starts, usually the thursday after the registration ends",
    )
    group_stage_start_monday = models.DateField(
        blank=True,
        help_text="Date when group stage starts, usually the next monday after the group stage starts",
    )
    group_stage_end = models.DateField(
        blank=True,
        help_text="Date when group stage ends, usually 11 weeks (81 days)",
    )
    playoffs_start = models.DateField(
        blank=True,
        help_text="Date when playoffs start, usually the monday after group stage ends",
    )
    playoffs_end = models.DateField(
        blank=True,
        help_text="Date when playoffs end, usually 2 weeks after playoffs start",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SplitManager()

    class Meta:
        db_table = "splits"
        verbose_name = "Split"
        verbose_name_plural = "Splits"

    def __str__(self):
        return self.name

    def in_range(self, d: datetime) -> bool:
        """
        Checks if the given datetime object is between the registration start and the playoffs end.
        :param d: datetime object
        :return: Returns True if the given datetime object is in the range of the split, False otherwise.
        """
        return self.registration_start <= d.date() <= self.playoffs_end

    def get_current_stage(self) -> Union[str, None]:
        current_date = timezone.now().date()
        if self.registration_start < current_date > self.playoffs_end:
            return None
        if self.playoffs_start <= current_date <= self.playoffs_end:
            return Match.MATCH_TYPE_PLAYOFF
        if self.group_stage_start <= current_date <= self.group_stage_end:
            return Match.MATCH_TYPE_LEAGUE
        if self.calibration_stage_start <= current_date <= self.calibration_stage_end:
            return Match.MATCH_TYPE_GROUP

    def get_current_match_day(self):
        current_date = timezone.now().date()
        return count_weeks(self.group_stage_start_monday, current_date)

    @staticmethod
    def calculate(registration_start: date, registration_end: date) -> dict:
        group_stage_start = registration_end + timedelta(days=1)
        group_stage_start_monday = get_next_monday(group_stage_start)
        group_stage_end = group_stage_start_monday + timedelta(days=76)
        d = {
            "registration_start": registration_start,
            "registration_end": registration_end,
            "calibration_stage_start": registration_end - timedelta(days=4),
            "calibration_stage_end": registration_end,
            "group_stage_start": group_stage_start,
            "group_stage_start_monday": group_stage_start_monday,
            "group_stage_end": group_stage_end,
            "playoffs_start": group_stage_end,
            "playoffs_end": group_stage_end + timedelta(days=15),
        }
        return d

    @property
    def prime_league_link(self) -> str:
        return f"{settings.MATCH_URI}{self.id}"


def get_next_monday(d):
    """
    https://stackoverflow.com/a/6558571/9498605
    :param d: date where to start
    :return: date of next monday
    """
    days_ahead = 0 - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

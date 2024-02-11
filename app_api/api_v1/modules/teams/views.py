from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django_filters.rest_framework import DjangoFilterBackend
from django_ical.views import ICalFeed
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from app_prime_league.models import Match, Team
from bots.messages.base import MatchMixin
from bots.messages.helpers import MatchDisplayHelper

from .serializers import TeamDetailSerializer, TeamSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    detail_serializer_class = TeamDetailSerializer
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_fields = [
        "division",
        "name",
        "team_tag",
    ]
    search_fields = ['name', 'team_tag', "division"]
    ordering = ['id']
    ordering_fields = ['id', 'name', "team_tag", "division", "updated_at"]
    throttle_scope = 'teams'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.annotate(_matches_count=Count("matches_against", distinct=True))
        return qs.prefetch_related(
            "matches_against",
            "matches_against__enemy_lineup",
            "matches_against__team_lineup",
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return self.serializer_class


class MatchEvent(MatchMixin):
    def __init__(self, match):
        self.match = match
        self.team = self.match.team

    def _schedule_status(self) -> str:
        """Returns an emoji based on the match status."""
        if self.match.match_begin_confirmed:
            return "⚔"
        if self.match.team_made_latest_suggestion is None or self.match.datetime_until_auto_confirmation is None:
            return "📆"
        if self.match.team_made_latest_suggestion:
            return "✅"
        return "⚠"

    def get_title(self):
        title = "[Prime League] {schedule_status} {match_day}: {team_tag} vs {enemy_team_name}"
        return escape(
            title.format(
                schedule_status=self._schedule_status(),
                match_day=MatchDisplayHelper.display_match_day(self.match).title(),
                team_tag=self.team.team_tag,
                enemy_team_name=self.match.get_enemy_team().name,
            )
        )

    def get_description(self):
        scouting_website = (
            settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        )
        enemy_scouting_url = self.team.get_scouting_url(match=self.match, lineup=False)
        description = (
            f"**{MatchDisplayHelper.display_match_day(self.match)}**\n"
            f"{MatchDisplayHelper.display_match_schedule_simple(self.match)}\n"
            f"🔍 {scouting_website}: {self.get_enemy_team_scouting_url(self.match)}\n"
            "Match URL: {prime_league_link}\n"
        )
        return escape(
            description.format(
                prime_league_link=self.match.prime_league_link,
                scouting_link=enemy_scouting_url,
            )
        )

    def get_start_datetime(self):
        return self.match.begin

    def get_end_datetime(self):
        return self.match.begin + timedelta(hours=2)

    def get_link(self):
        return self.match.prime_league_link

    def get_guid(self):
        return f"{self.team.id}_{self.match.id}@primebot.me"


class TeamMatchesFeed(ICalFeed):
    product_id = '-//primebot.me//team-matches//EN'
    timezone = 'UTC'

    def file_name(self, obj) -> str:
        return f"{obj.id}_matches.ics"

    def item_guid(self, item: MatchEvent) -> str:
        return item.get_guid()

    def get_object(self, request, *args, **kwargs) -> Team:
        team = get_object_or_404(Team, pk=kwargs["pk"])
        return team

    def items(self, obj) -> list[MatchEvent]:
        return [MatchEvent(match) for match in Match.current_split_objects.filter(team=obj).order_by('-begin')]

    def item_title(self, item: MatchEvent):
        return item.get_title()

    def item_description(self, item: MatchEvent):
        return item.get_description()

    def item_start_datetime(self, item: MatchEvent):
        return item.get_start_datetime()

    def item_end_datetime(self, item: MatchEvent):
        return item.get_end_datetime()

    def item_link(self, item: MatchEvent):
        return item.get_link()

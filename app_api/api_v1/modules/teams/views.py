from datetime import timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_ical.views import ICalFeed
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from app_prime_league.models import Match, Team

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


class TeamMatchesFeed(ICalFeed):
    product_id = '-//primebot.me//team-matches//EN'
    timezone = 'UTC'
    file_name = ".ics"

    def get_object(self, request, *args, **kwargs):
        return get_object_or_404(Team, pk=kwargs["pk"])

    def items(self, obj):
        return obj.matches_against.all().order_by('begin')

    def item_title(self, item: Match):
        if item.enemy_team is None:
            return f"{item.team.name} vs TBD"
        return f"{item.team.name} vs {item.enemy_team.name}"

    def item_description(self, item):
        return "desc"

    def item_start_datetime(self, item):
        return item.begin

    def item_end_datetime(self, item):
        return item.begin + timedelta(hours=2)

    def item_link(self, item):
        return "www.primebot.me"

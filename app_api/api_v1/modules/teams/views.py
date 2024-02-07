from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from django_ical.views import ICalFeed
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from app_prime_league.models import Team

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
    """
    A simple event calender
    """

    product_id = '-//primebot.me//team-matches//EN'
    timezone = 'UTC'
    file_name = "event.ics"

    def items(self):
        return self.team.matches_against.objects.all().order_by('-start_datetime')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start_datetime

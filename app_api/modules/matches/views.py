from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from app_prime_league.models import Match

from .serializers import MatchDetailSerializer, MatchSerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    detail_serializer_class = MatchDetailSerializer
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_fields = [
        "match_day",
        "match_type",
        "team",
        "enemy_team",
        "team_made_latest_suggestion",
        "match_begin_confirmed",
        "has_side_choice",
        "closed",
        "result",
    ]
    search_fields = ['team__name', 'team__team_tag']
    ordering = ["match_id"]
    ordering_fields = [
        'match_id',
        'match_day',
        "match_type",
        "team__name",
        "begin",
        "closed",
        "result",
        "datetime_until_auto_confirmation",
        "match_begin_confirmed",
        "updated_at",
    ]
    throttle_scope = 'matches'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "team",
            "enemy_team",
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return self.serializer_class

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from app_prime_league.models import Match

from .serializers import MatchDetailSerializer, MatchSerializer


class MatchByMatchIDSerializerIn(serializers.Serializer):
    team_id = serializers.IntegerField(required=True)
    match_id = serializers.IntegerField(required=True)


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

    @extend_schema(
        parameters=[MatchByMatchIDSerializerIn],
    )
    @action(detail=False, url_path="by-match-id")
    def by_match_id(self, request, *args, **kwargs):
        serializer_in = MatchByMatchIDSerializerIn(data=request.query_params)
        serializer_in.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())
        instance = get_object_or_404(queryset, **serializer_in.validated_data)
        self.check_object_permissions(self.request, instance)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

from rest_framework import viewsets

from app_prime_league.models import Match

from .serializers import MatchDetailSerializer, MatchSerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    detail_serializer_class = MatchDetailSerializer

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

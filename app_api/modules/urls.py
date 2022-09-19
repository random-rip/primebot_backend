from django.urls import path
from rest_framework.routers import SimpleRouter

from app_api.modules.matches.views import MatchViewSet
from app_api.modules.teams.views import TeamViewSet
from app_api.modules.views import api_root

router = SimpleRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matches', MatchViewSet, basename='match')

urlpatterns = [
    path('', api_root)
]

urlpatterns += router.urls

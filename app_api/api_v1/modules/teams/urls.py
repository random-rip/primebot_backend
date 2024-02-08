from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import TeamMatchesFeed, TeamViewSet

router = SimpleRouter()
router.register('teams', TeamViewSet, basename='team')

urlpatterns = [
    path('teams/<int:pk>/ics', TeamMatchesFeed(), name='team-matches-feed'),
] + router.urls

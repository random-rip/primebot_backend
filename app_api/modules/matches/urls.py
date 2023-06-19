from rest_framework.routers import SimpleRouter

from app_api.modules.matches.views import MatchViewSet

router = SimpleRouter()
router.register(r'matches', MatchViewSet, basename='match')

urlpatterns = router.urls

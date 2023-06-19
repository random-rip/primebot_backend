from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', include("app_api.modules.team_settings.urls")),
    path('', include("app_api.modules.status.urls")),
    path('', include("app_api.modules.teams.urls")),
    path('', include("app_api.modules.matches.urls")),
    path('', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('schema', SpectacularAPIView.as_view(), name='schema'),
]

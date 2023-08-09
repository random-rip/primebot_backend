from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', include("app_api.api_v1.modules.team_settings.urls")),
    path('', include("app_api.api_v1.modules.status.urls")),
    path('', include("app_api.api_v1.modules.teams.urls")),
    path('', include("app_api.api_v1.modules.matches.urls")),
    path('', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('schema', SpectacularAPIView.as_view(api_version="v1"), name='schema'),
]

from django.urls import path, include

urlpatterns = [
    path('settings/', include("app_api.modules.team_settings.urls"), )
]

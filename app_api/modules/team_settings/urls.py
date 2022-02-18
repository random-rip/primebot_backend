from django.conf import settings
from django.urls import path

from app_api.modules.team_settings import views

urlpatterns = [
    path('', views.SettingsView.as_view(), ),
]
if settings.DEBUG:
    urlpatterns += [
        path('create/', views.create, )
    ]

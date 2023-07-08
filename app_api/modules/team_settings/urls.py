from django.urls import path

from app_api.modules.team_settings import views

urlpatterns = [
    path('settings/', views.SettingsView.as_view()),
]

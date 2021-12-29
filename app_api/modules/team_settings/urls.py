from django.urls import path

from app_api import views

urlpatterns = [
    path('', views.SettingsView.as_view(), )
]

from django.urls import path

from app_api.modules.status import views

urlpatterns = [
    path('status/', views.StatusView.as_view()),
    path('status/changelogs/', views.ChangelogView.as_view()),
]

from django.urls import path

from .views import ChangelogView, StatusView

urlpatterns = [
    path('status/', StatusView.as_view()),
    path('status/changelogs/', ChangelogView.as_view()),
]

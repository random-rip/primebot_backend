from django.urls import path

from quicklinks_admin.send_teams_message.views import ClearTeamsMessageView, ConfirmTeamsMessageView, TeamsMessageView

urlpatterns = [
    path('clear-teams-message/', ClearTeamsMessageView.as_view(), name='clear-teams-message'),
    path('send-teams-message/', TeamsMessageView.as_view(), name='send-teams-message'),
    path('confirm-send-teams-message/', ConfirmTeamsMessageView.as_view(), name='confirm-teams-message'),
]

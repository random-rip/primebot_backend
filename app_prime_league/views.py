import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.views.generic import TemplateView

from app_prime_league.models import Team
from communication_interfaces import send_message


class GlobalMessage(LoginRequiredMixin, TemplateView, ):
    template_name = 'global_message.html'

    def get(self, request, *args, **kwargs):
        context = {"time": datetime.datetime.now()}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        msg = request.POST["message"]
        teams = Team.objects.exclude(telegram_id__isnull=True)
        for team in teams:
            msg = msg.format(team_tag=team.team_tag, )
            send_message(msg=msg, chat_id=team.telegram_id)
        return render(request, self.template_name)

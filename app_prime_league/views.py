import datetime

import telepot
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

from app_prime_league.models import Team
from telegram_interface import send_message


class GlobalMessage(TemplateView, LoginRequiredMixin, ):
    template_name = 'global_message.html'

    def get(self, request, *args, **kwargs):
        context = {"time": datetime.datetime.now()}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        msg = request.POST["message"]
        teams = Team.objects.exclude(telegram_channel_id__isnull=True)
        for team in teams:
            send_message(msg=msg, chat_id=team.telegram_channel_id)
        return render(request, self.template_name)

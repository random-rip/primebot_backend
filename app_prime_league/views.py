import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class GlobalMessage(LoginRequiredMixin, TemplateView, ):
    template_name = 'global_message.html'

    def get(self, request, *args, **kwargs):
        context = {"time": datetime.datetime.now()}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        msg = request.POST["message"]
        print(msg)
        return render(request, self.template_name)
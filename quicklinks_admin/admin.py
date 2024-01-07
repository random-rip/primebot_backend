from django.contrib import admin
from django.urls import path

from .models import Quicklink
from .views import TeamsMessageView


class QuicklinkAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['quicklinks'] = Quicklink.objects.all()
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('teams-message/', self.admin_view(TeamsMessageView.as_view()), name='teams-message'),
        ]
        return custom_urls + urls


admin.site = QuicklinkAdminSite(name='admin')
admin.site.register(Quicklink)

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.urls import include, path

from .models import Quicklink


class QuicklinkAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['quicklinks'] = Quicklink.objects.filter(is_active=True).order_by('order', 'title')
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "",
                include(
                    ("quicklinks_admin.send_teams_message.urls", "send_teams_message"), namespace='send-teams-message'
                ),
            ),
        ]
        return custom_urls + urls


admin.site = QuicklinkAdminSite(name='admin')
admin.site.register(Quicklink)

User = get_user_model()
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)

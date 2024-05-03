from admin_interface.admin import ThemeAdmin
from admin_interface.models import Theme
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.urls import include, path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Quicklink


class QuicklinkAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['quicklinks'] = self.get_quicklinks(request)
        return super().index(request, extra_context=extra_context)

    def get_quicklinks(self, request):
        if request.user.is_superuser:
            return Quicklink.objects.filter(is_active=True).order_by('order', 'title')
        return Quicklink.objects.filter(is_active=True, groups__in=request.user.groups.all()).order_by('order', 'title')

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


admin.site.unregister(Theme)
admin.site = QuicklinkAdminSite(name='admin')

User = get_user_model()
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Theme, ThemeAdmin)


class QuicklinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', "to_url", 'is_active', 'order')
    list_filter = ('is_active', 'groups')
    search_fields = ('title', 'url')
    filter_horizontal = ('groups',)

    def to_url(self, obj: Quicklink):
        disabled_attr = 'disabled' if not obj.is_active else ''
        return format_html('<a class="button" href="{}" target="_blank" {}>Zur PL</a>&nbsp;', obj.url, disabled_attr)

    to_url.allow_tags = True
    to_url.short_description = _("To Page")


admin.site.register(Quicklink, QuicklinkAdmin)

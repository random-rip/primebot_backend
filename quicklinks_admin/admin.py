from django.contrib import admin

from .models import Quicklink

# Register your models here.


class QuicklinkAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['quicklinks'] = Quicklink.objects.all()
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        return urls


admin.site = QuicklinkAdminSite(name='admin')
admin.site.register(Quicklink)

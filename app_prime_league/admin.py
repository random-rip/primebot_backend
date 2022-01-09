from django.contrib import admin

from .models import Changelog

class ChangelogAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields': ['version_number']}),
        (None,      {'fields': ['description']}),
    ]
    list_display = ('version_number', 'created_at', 'updated_at')
    list_filter = ['created_at']
    search_fields = ['version_number']

admin.site.register(Changelog, ChangelogAdmin)

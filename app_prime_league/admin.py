from django.contrib import admin

from app_prime_league.models import Team, Player, Match, ScoutingWebsite, Suggestion, Setting, SettingsExpiring, Comment

admin.site.register(Team, )
admin.site.register(Player, )
admin.site.register(Match, )
admin.site.register(ScoutingWebsite, )
admin.site.register(Suggestion, )
admin.site.register(Setting, )
admin.site.register(SettingsExpiring, )
admin.site.register(Comment, )

class ChangelogAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields': ['version_number']}),
        (None,      {'fields': ['description']}),
    ]
    list_display = ('version_number', 'created_at', 'updated_at')
    list_filter = ['created_at']
    search_fields = ['version_number']

admin.site.register(Changelog, ChangelogAdmin)

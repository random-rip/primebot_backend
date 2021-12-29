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

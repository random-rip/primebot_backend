from django.contrib import admin

from app_prime_league.admin_sites.champions import ChampionAdmin
from app_prime_league.admin_sites.changelog import ChangelogAdmin
from app_prime_league.admin_sites.comment import CommentAdmin
from app_prime_league.admin_sites.match import MatchAdmin
from app_prime_league.admin_sites.player import PlayerAdmin
from app_prime_league.admin_sites.scouting_website import ScoutingWebsiteAdmin
from app_prime_league.admin_sites.team import TeamAdmin
from app_prime_league.admin_sites.team_settings import SettingsExpiringAdmin, SettingAdmin
from app_prime_league.models import Player, Match, ScoutingWebsite, Suggestion, Comment, Team, Changelog, Setting, \
    SettingsExpiring, Champion

admin.site.register(Player, PlayerAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(ScoutingWebsite, ScoutingWebsiteAdmin)
admin.site.register(Suggestion, )
admin.site.register(Comment, CommentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Changelog, ChangelogAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(SettingsExpiring, SettingsExpiringAdmin)
admin.site.register(Champion, ChampionAdmin)

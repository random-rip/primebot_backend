from django.contrib import admin
from django_q.models import Failure, Schedule, Success

from app_prime_league.admin_sites.champions import ChampionAdmin
from app_prime_league.admin_sites.comment import CommentAdmin
from app_prime_league.admin_sites.djangoq2 import FailAdmin, ScheduleAdmin, TaskAdmin
from app_prime_league.admin_sites.match import MatchAdmin, SuggestionAdmin
from app_prime_league.admin_sites.player import PlayerAdmin
from app_prime_league.admin_sites.scouting_website import ScoutingWebsiteAdmin
from app_prime_league.admin_sites.split import SplitAdmin
from app_prime_league.admin_sites.team import TeamAdmin
from app_prime_league.admin_sites.team_settings import SettingAdmin, SettingsExpiringAdmin
from app_prime_league.models import (
    Champion,
    Comment,
    Match,
    Player,
    ScoutingWebsite,
    Setting,
    SettingsExpiring,
    Split,
    Suggestion,
    Team,
)

admin.site.register(Player, PlayerAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(ScoutingWebsite, ScoutingWebsiteAdmin)
admin.site.register(Suggestion, SuggestionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(SettingsExpiring, SettingsExpiringAdmin)
admin.site.register(Champion, ChampionAdmin)
admin.site.register(Split, SplitAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Success, TaskAdmin)
admin.site.register(Failure, FailAdmin)

from django.contrib import admin


class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'match_day', 'match_type', 'team', 'enemy_team', 'begin', 'closed', 'result',
                    'created_at', 'updated_at', 'suggestion_set']
    list_filter = ['match_day', 'match_type', 'created_at', 'updated_at', 'begin']
    search_fields = ['team__id', 'team__name', 'enemy_team__id', 'enemey_team__name', 'match_id']

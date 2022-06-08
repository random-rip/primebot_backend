from django.contrib import admin


class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'match_day', 'match_type', 'team', 'enemy_team', 'begin', 'closed', 'result',
                    'created_at', 'updated_at', ]
    list_filter = ['match_day', 'match_type', 'created_at', 'updated_at', 'begin']
    readonly_fields = ("created_at", "updated_at",)
    filter_vertical = ("enemy_lineup", "team_lineup",)
    search_fields = ['team__id', 'team__name', 'enemy_team__id', 'enemy_team__name', 'match_id']


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'begin', 'match', 'created_at']

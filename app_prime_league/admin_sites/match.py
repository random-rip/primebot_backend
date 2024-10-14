from django.contrib import admin
from django.utils.html import format_html


class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'match_id',
        'match_day',
        'match_type',
        'team',
        'enemy_team',
        'begin',
        'closed',
        "prime_league_link",
        "split",
        'result',
        'created_at',
        'updated_at',
    ]
    list_filter = ['match_day', 'match_type', 'created_at', 'updated_at', 'begin', "split"]
    raw_id_fields = ["team", "enemy_team"]
    readonly_fields = (
        "created_at",
        "updated_at",
        "enemy_lineup",
        "team_lineup",
    )
    filter_vertical = (
        "enemy_lineup",
        "team_lineup",
    )
    search_fields = ['team__id', 'team__name', 'enemy_team__id', 'enemy_team__name', 'match_id']

    @admin.display(description="Prime League")
    def prime_league_link(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Zur PL</a>&nbsp;',
            obj.prime_league_link,
        )


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'begin', 'match', 'created_at']

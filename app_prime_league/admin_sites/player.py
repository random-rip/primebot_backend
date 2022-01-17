from django.contrib import admin


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'summoner_name', 'is_leader', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'is_leader']
    search_fields = ['name', 'team__id', 'team__name', 'summoner_name']

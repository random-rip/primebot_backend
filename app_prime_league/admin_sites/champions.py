from django.contrib import admin


class ChampionAdmin(admin.ModelAdmin):
    list_display = ('name', 'banned', 'banned_until', 'banned_until_patch', 'created_at', 'updated_at')
    list_filter = ['banned_until_patch', 'created_at', 'updated_at']
    search_fields = ['name', 'banned_until_patch']

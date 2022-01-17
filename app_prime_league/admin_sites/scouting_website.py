from django.contrib import admin


class ScoutingWebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'separator', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'name']
    search_fields = ['name', 'base_url']

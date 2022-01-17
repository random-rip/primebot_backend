from django.contrib import admin


class ChangelogAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['version_number']}),
        (None, {'fields': ['description']}),
    ]
    list_display = ('version_number', 'truncated_description', 'created_at', 'updated_at')
    list_filter = ['created_at', 'updated_at']
    search_fields = ['version_number', 'description']

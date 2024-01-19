from django.contrib import admin


class SettingsExpiringAdmin(admin.ModelAdmin):
    list_display = ('team', 'expires', 'created_at', 'updated_at')
    list_filter = ['created_at']
    search_fields = ['team__id', 'team__name']
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class SettingAdmin(admin.ModelAdmin):
    list_display = ('team', 'attr_name', 'attr_value', 'created_at', 'updated_at')
    list_filter = ['created_at', 'attr_name']
    search_fields = ['team__id', 'team__name']
    readonly_fields = (
        "created_at",
        "updated_at",
    )

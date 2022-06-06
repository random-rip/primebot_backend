from django.contrib import admin
from django.db.models import Q


class PlatformFilter(admin.SimpleListFilter):
    title = 'Platform'
    parameter_name = 'platform'

    def lookups(self, request, model_admin):
        return (
            ('discord', 'Discord'),
            ('telegram', 'Telegram'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'discord':
            return queryset.filter(discord_channel_id__isnull=False)
        if self.value() == 'telegram':
            return queryset.filter(telegram_id__isnull=False)
        return queryset


class RegisterFilter(admin.SimpleListFilter):
    title = 'Team ist Registriert'
    parameter_name = 'registered'

    def lookups(self, request, model_admin):
        return (
            ("registered", 'Nur registrierte Teams'),
            ("not_registered", 'Nur nicht registrierte Teams'),
            ("not_registered_and_no_division", 'Nur nicht registrierte Teams ohne Division'),
        )

    def queryset(self, request, queryset):
        if self.value() == "registered":
            return queryset.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))
        if self.value() == "not_registered":
            return queryset.filter(telegram_id__isnull=True, discord_channel_id__isnull=True)
        if self.value() == "not_registered_and_no_division":
            return queryset.filter(telegram_id__isnull=True, discord_channel_id__isnull=True, division__isnull=True)
        return queryset


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'team_tag',
        'division',
        'discord_registered',
        'telegram_registered',
        'scouting_website',
        'created_at',
        'updated_at',
    )
    list_filter = [PlatformFilter, RegisterFilter, 'created_at', 'updated_at', ]
    readonly_fields = ("created_at", "updated_at",)
    search_fields = ['id', 'name', 'team_tag']

    def discord_registered(self, obj):
        return bool(obj.discord_webhook_token)

    discord_registered.boolean = True

    def telegram_registered(self, obj):
        return bool(obj.telegram_id)

    telegram_registered.boolean = True

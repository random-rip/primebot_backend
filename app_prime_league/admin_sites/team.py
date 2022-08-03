from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html


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
            ("active_teams", 'Nur aktive Teams'),
        )

    def queryset(self, request, queryset):
        if self.value() == "registered":
            return queryset.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))
        if self.value() == "not_registered":
            return queryset.filter(telegram_id__isnull=True, discord_channel_id__isnull=True)
        if self.value() == "not_registered_and_no_division":
            return queryset.filter(telegram_id__isnull=True, discord_channel_id__isnull=True, division__isnull=True)
        if self.value() == "active_teams":
            return queryset.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False),
                                   division__isnull=False)
        return queryset


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'team_tag',
        'division',
        'discord_registered',
        'telegram_registered',
        "prime_league_link",
        'scouting_website',
        'language',
        'created_at',
        'updated_at',
    )
    list_filter = [PlatformFilter, RegisterFilter, 'language', 'created_at', 'updated_at', ]
    readonly_fields = ("created_at", "updated_at",)
    search_fields = ['id', 'name', 'team_tag']

    def prime_league_link(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Zur PL</a>&nbsp;',
            f"{settings.TEAM_URI}{obj.id}",
        )

    prime_league_link.allow_tags = True
    prime_league_link.short_description = "Prime League"

    def discord_registered(self, obj):
        return bool(obj.discord_webhook_token)

    discord_registered.boolean = True
    discord_registered.short_description = "Discord"

    def telegram_registered(self, obj):
        return bool(obj.telegram_id)

    telegram_registered.boolean = True
    telegram_registered.short_description = "Telegram"

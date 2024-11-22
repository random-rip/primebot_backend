from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app_prime_league.models import Match, Player


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
            return queryset.filter(
                Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False), division__isnull=False
            )
        return queryset


class PlayersFilter(admin.SimpleListFilter):

    title = _("Players")
    parameter_name = "no_players"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("With Players")),
            ("no", _("Without Players")),
        )

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.annotate(num_players=Count("player")).filter(num_players=0)
        if self.value() == "yes":
            return queryset.annotate(num_players=Count("player")).exclude(num_players=0)
        return queryset


class PlayerInline(admin.TabularInline):
    ordering = ("name",)
    model = Player
    classes = ("collapse",)
    extra = 0
    fields = (
        "id",
        "name",
        "summoner_name",
        "is_leader",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MatchInline(admin.TabularInline):
    ordering = ("match_type", "match_day", "closed")
    model = Match
    classes = ("collapse",)
    extra = 0
    show_change_link = True
    fk_name = "team"
    fields = (
        "match_id",
        "match_day",
        "match_type",
        "enemy_team",
        "begin",
        "closed",
        "result",
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MatchAsEnemyInline(MatchInline):
    fk_name = "enemy_team"
    verbose_name = "Matches as Enemy"
    verbose_name_plural = "Matches as Enemy"
    fields = (
        "match_id",
        "match_day",
        "match_type",
        "team",
        "begin",
        "closed",
        "result",
    )


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline,
        MatchInline,
        MatchAsEnemyInline,
    ]
    list_display_links = ("id", "name")
    list_display = (
        'id',
        'name',
        'team_tag',
        'division',
        'discord_registered',
        'telegram_registered',
        "prime_league_link",
        "split",
        'scouting_website',
        'language',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "name",
                    ("prime_league_link",),
                    ("team_tag",),
                    ("division",),
                    ("split",),
                    ("created_at",),
                    ("updated_at",),
                ),
            },
        ),
        (
            "Registered Infos",
            {
                "fields": (
                    ("discord_registered",),
                    ("telegram_registered",),
                    ("logo_url",),
                    ("scouting_website",),
                    ("language",),
                ),
            },
        ),
        (
            "Discord",
            {
                "fields": (
                    ("discord_webhook_id",),
                    ("discord_webhook_token",),
                    ("discord_guild_id",),
                    ("discord_channel_id",),
                    ("discord_role_id",),
                ),
                "classes": ("collapse",),
            },
        ),
        ("Telegram", {"fields": (("telegram_id",),), "classes": ("collapse",)}),
    )

    list_filter = [
        PlatformFilter,
        RegisterFilter,
        PlayersFilter,
        'language',
        'created_at',
        'updated_at',
        "split",
    ]
    readonly_fields = ("created_at", "updated_at", "discord_registered", "telegram_registered", "prime_league_link")
    search_fields = ['id', 'name', 'team_tag']

    @admin.display(description="Prime League")
    def prime_league_link(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Zur PL</a>&nbsp;',
            obj.prime_league_link,
        )

    @admin.display(boolean=True, description='Discord')
    def discord_registered(self, obj):
        return bool(obj.discord_channel_id)

    @admin.display(
        boolean=True,
        description='Telegram',
    )
    def telegram_registered(self, obj):
        return bool(obj.telegram_id)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("split")

from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app_prime_league.models import Match, Player, Team
from app_prime_league.models.channel import Platforms


class PlatformFilter(admin.SimpleListFilter):
    title = _('Platform')
    parameter_name = 'platform'

    def lookups(self, request, model_admin):
        return (
            ('discord', 'Discord'),
            ('telegram', 'Telegram'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'discord':
            return queryset.filter(_subscribers_on_discord__gt=0)
        if self.value() == 'telegram':
            return queryset.filter(_subscribers_on_telegram__gt=0)
        return queryset


class SubscriptionFilter(admin.SimpleListFilter):
    title = _("Team has Subscriptions")
    parameter_name = 'subscriptions'

    def lookups(self, request, model_admin):
        return (
            ("subscriptions", _("Only subscribed Teams")),
            ("no_subscriptions", _('Only not subscribed Teams')),
        )

    def queryset(self, request, queryset):
        if self.value() == "subscriptions":
            return queryset.filter(_subscribers__gt=0)
        if self.value() == "no_subscriptions":
            return queryset.filter(_subscribers=0)
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


class ChannelInline(admin.TabularInline):
    verbose_name = _("Channel")
    verbose_name_plural = _("Channels")
    model = Team.channels.through
    extra = 0
    show_change_link = True
    fields = (
        "channel",
        "channel__platform",
        "_channel_id",
        "created_at",
        "updated_at",
    )
    readonly_fields = fields

    @admin.display(description=_("Platform"))
    def channel__platform(self, obj):
        return obj.channel.platform

    @admin.display(description=_("Channel ID"))
    def _channel_id(self, obj):
        return obj.channel.get_real_channel_id()

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        ChannelInline,
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
        "_subscribers",
        '_subscribers_on_discord',
        '_subscribers_on_telegram',
        "prime_league_link",
        "split",
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            _("General"),
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
            _("Subscription Infos"),
            {
                "fields": (
                    ("_subscribers",),
                    ("_subscribers_on_discord",),
                    ("_subscribers_on_telegram",),
                ),
            },
        ),
    )

    list_filter = [
        PlatformFilter,
        SubscriptionFilter,
        PlayersFilter,
        'created_at',
        'updated_at',
        "split",
    ]
    readonly_fields = (
        "created_at",
        "updated_at",
        "_subscribers_on_discord",
        "_subscribers_on_telegram",
        "_subscribers",
        "prime_league_link",
    )
    search_fields = ['id', 'name', 'team_tag']

    @admin.display(description="Prime League")
    def prime_league_link(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Zur PRM</a>&nbsp;',
            obj.prime_league_link,
        )

    @admin.display(description=_("Subscribers on Discord"), ordering='_subscribers_on_discord')
    def _subscribers_on_discord(self, obj: Team):
        return obj._subscribers_on_discord

    @admin.display(description=_("Subscribers on Telegram"), ordering='_subscribers_on_telegram')
    def _subscribers_on_telegram(self, obj: Team):
        return obj._subscribers_on_telegram

    @admin.display(description=_('Subscribers'), ordering='_subscribers')
    def _subscribers(self, obj: Team):
        return obj._subscribers

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("split")
            .annotate(
                _subscribers_on_discord=Count("channels", filter=Q(channels__platform=Platforms.DISCORD)),
                _subscribers_on_telegram=Count("channels", filter=Q(channels__platform=Platforms.TELEGRAM)),
                _subscribers=Count("channels"),
            )
        )

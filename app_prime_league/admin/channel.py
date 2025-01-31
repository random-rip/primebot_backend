from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from app_prime_league.models import Setting, Team


class SettingInline(admin.TabularInline):
    model = Setting
    verbose_name = _("Setting")
    verbose_name_plural = _("Settings")
    fields = (
        "attr_name",
        "attr_value",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    extra = 0
    ordering = ("attr_name",)

    def get_queryset(self, request):
        return super().get_queryset(request)


class ChannelTeamAdmin(admin.ModelAdmin):
    list_display = ('team', 'channel', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('team__id', 'team__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        SettingInline,
    ]


class TeamInline(admin.TabularInline):
    model = Team.channels.through
    verbose_name = _("Subscribed Team")
    verbose_name_plural = _("Subscribed Teams")
    fields = (
        "team",
        "_team_tag",
        "_division",
        "_split",
        "created_at",
    )
    readonly_fields = fields
    extra = 0
    show_change_link = True

    @admin.display(description="Tag")
    def _team_tag(self, obj):
        return obj.team.team_tag

    @admin.display(description="Division")
    def _division(self, obj):
        return obj.team.division or "-"

    @admin.display(description="Split")
    def _split(self, obj):
        return obj.team.split or "-"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("team").order_by("team__id")


class ChannelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "platform",
        "_channel_id",
        "_teams_count",
        "name",
        "scouting_website",
        "language",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "platform")
    list_filter = (
        'platform',
        "scouting_website",
        "language",
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "platform",
                    "_channel_id",
                    "name",
                    "_teams_count",
                    "scouting_website",
                    "language",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Discord",
            {
                "fields": (
                    "discord_guild_id",
                    "discord_webhook_id",
                    "discord_webhook_token",
                    "discord_channel_id",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Telegram",
            {
                "fields": ("telegram_id",),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "_channel_id",
        "_teams_count",
    )
    inlines = [
        TeamInline,
    ]

    @admin.display(description=_("Channel ID"))
    def _channel_id(self, obj):
        return obj.get_real_channel_id()

    @admin.display(description=_("Subscribed Teams"))
    def _teams_count(self, obj):
        return obj._teams_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_teams_count=Count("channel_teams"))
            .select_related("scouting_website")
        )

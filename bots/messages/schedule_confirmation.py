import logging

from django.conf import settings
from django.utils.translation import gettext as _
from telegram import ParseMode

from app_prime_league.models import ChannelTeam, Match
from bots.messages.base import MatchMessage
from bots.telegram_interface.tg_singleton import send_message_to_devs
from core.parsing.logs import LogChangeTime, LogSchedulingAutoConfirmation
from utils.utils import format_datetime


class ScheduleConfirmationNotification(MatchMessage):
    settings_key = "SCHEDULING_CONFIRMATION"
    mentionable = True

    def __init__(self, channel_team: ChannelTeam, match: Match, latest_confirmation_log):
        super().__init__(channel_team=channel_team, match=match)
        self.latest_confirmation_log = latest_confirmation_log

    def _generate_title(self):
        return "⚔ " + _("Confirmation of the scheduled date")

    def _generate_message(self):
        time = format_datetime(self.match.begin)
        enemy_team_tag = self.match.enemy_team.team_tag

        if isinstance(self.latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = _(
                "Automatic confirmation of the scheduled date against [{enemy_team_tag}]"
                "({enemy_team_url}) for [{match_day}]({match_url}):"
            )
        elif isinstance(self.latest_confirmation_log, LogChangeTime):
            message = _(
                "An administrator has set a new date for [{match_day}]({match_url}) "
                "against [{enemy_team_tag}]({enemy_team_url}):"
            )
        else:
            if self.latest_confirmation_log is None:
                msg = (
                    f"WTF why is the latest_confirmation_log None? It should be LogSchedulingConfirmation.\n"
                    f"This happened in Match {self.match}. May be some delayed logs from PLM side?"
                )
                logging.getLogger("notifications").error(msg)
                send_message_to_devs(msg, parse_mode=ParseMode.MARKDOWN)

            message = _(
                "Confirmation of the scheduled date against [{enemy_team_tag}]"
                "({enemy_team_url}) for [{match_day}]({match_url}):"
            )

        return (message + "\n⚔{time}").format(
            time=time,
            enemy_team_tag=enemy_team_tag,
            match_url=f"{settings.MATCH_URI}{self.match.match_id}",
            enemy_team_url=f"{settings.TEAM_URI}{self.match.enemy_team.id}",
            match_day=self.match_helper.display_match_day(self.match),
        )

    def discord_hooks(self):
        if self.channel_team.value_of_setting(
            "CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION",
            default=False,
        ):
            from bots.discord_interface.create_event import CreateDiscordEventJob

            CreateDiscordEventJob(self.channel_team, self.match).enqueue()

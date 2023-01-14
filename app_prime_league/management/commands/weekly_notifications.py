import logging

from django_q.models import Schedule

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import WeeklyNotificationMessage
from core.commands import ScheduleCommand
from utils.utils import current_match_day


class Command(ScheduleCommand):
    @staticmethod
    def func():
        match_day = current_match_day()

        logger = logging.getLogger("notifications")
        logger.info(f"Start Sending Weekly Notifications...")
        teams = Team.objects.get_registered_teams()
        for team in teams:
            try:
                next_match = team.matches_against.filter(match_day=match_day).last()
                if next_match is not None:
                    logger.debug(f"Sending Weekly Notification to {team}...")
                    MessageCollector(team=team).dispatch(WeeklyNotificationMessage, match=next_match)
            except Exception as e:
                logger.exception(f"Error sending weekly notification to team {team}: {e}")

    def _schedule(self):
        s = Schedule(
            name="Weekly Notifications",
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='0 9 * * mon',
        )
        s.next_run = s.calculate_next_run()
        s.save()

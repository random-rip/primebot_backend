import logging
from datetime import timedelta

from django.utils import timezone
from django_q.models import Schedule

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCreatorJob
from bots.messages import WeeklyNotificationMessage
from core.commands import ScheduleCommand


class Command(ScheduleCommand):
    @staticmethod
    def func():
        logger = logging.getLogger("notifications")
        logger.info("Start Sending Weekly Notifications...")
        lower_bound = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        upper_bound = lower_bound + timedelta(days=7)
        teams = (
            Team.objects.get_registered_teams()
            .filter(
                matches_against__closed=False,
                matches_against__begin__gte=lower_bound,
                matches_against__begin__lte=upper_bound,
            )
            .distinct()
        )
        for team in teams:
            try:
                logger.info(f"Sending Weekly Notification to {team}...")
                MessageCreatorJob(msg_class=WeeklyNotificationMessage, team=team).enqueue()
            except Exception as e:
                logger.exception(f"Error sending weekly notification to team {team}: {e}")

    def _schedule(self):
        s = Schedule(
            name="Weekly Notifications",
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='0 9 * * mon',
            cluster="messages",
        )
        s.next_run = s.calculate_next_run()
        s.save()

import logging

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
        teams = Team.objects.get_registered_teams()
        for team in teams:
            if len(WeeklyNotificationMessage(team=team).matches) < 1:
                continue
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
        )
        s.next_run = s.calculate_next_run()
        s.save()

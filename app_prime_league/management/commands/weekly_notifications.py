import logging

from django.core.management import BaseCommand

from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import WeeklyNotificationMessage
from utils.utils import current_match_day


class Command(BaseCommand):
    def handle(self, *args, **options):
        match_day = current_match_day()

        logger = logging.getLogger("notifications")
        logger.info(f"Start Sending Weekly Notifications...")
        teams = Team.objects.get_registered_team_of_current_split()
        for team in teams:
            self.stdout.write(self.style.SUCCESS(f"{team}"))
            try:
                next_match = team.matches_against.filter(match_day=match_day).last()
                if next_match is not None:
                    logger.debug(f"Sending Weekly Notification to {team}...")
                    MessageDispatcher(team=team).dispatch(WeeklyNotificationMessage, match=next_match)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{e}"))
                logger.exception(f"Error {team}: {e}")

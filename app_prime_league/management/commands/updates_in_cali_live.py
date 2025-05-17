import logging
import time
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from app_prime_league.models import Match, Split, Team
from core.update_schedule_command import UpdateScheduleCommand
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

logger = logging.getLogger("updates")


class Command(UpdateScheduleCommand):
    help = """Update teams and matches that are in the calibration phase."""
    next_command = "updates_between_calibration_and_group_stage"
    name = "Update Teams and Matches in Calibration Stage"

    @staticmethod
    def func(notify=True):

        teams = (
            Team.objects.annotate(matches_count=Count("matches_against"))
            .filter(
                matches_count__gt=0,
            )
            .order_by("updated_at")
        )
        top_50_teams = teams[:50]
        start_time = time.time()
        logger.info(f"Updating {len(top_50_teams)} (of {len(teams)}) teams...")
        update_teams(teams=top_50_teams, notify=notify)
        logger.info(f"Updated {len(top_50_teams)} teams in {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        matches = Match.current_split_objects.get_matches_to_update(buffer=timedelta(hours=1, minutes=15)).order_by(
            "updated_at"
        )
        top_50_matches = matches[:50]
        logger.info(f"Checking {len(top_50_matches)} (of {len(matches)}) uncompleted matches...")
        update_uncompleted_matches(matches=top_50_matches, notify=notify)
        logger.info(f"Checked {len(top_50_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
        return {
            "TEAMS": [str(x) for x in top_50_teams],
            "MATCHES": [str(x) for x in top_50_matches],
        }

    @staticmethod
    def is_time_exceeded() -> bool:
        """
        Returns True if the calibration stage ended (two days after calibration stage start)
        :return: True if the calibration stage ended
        """
        # We use a different calibration end here because the calibration stage ends 2 days after the calibration
        # stage start. The default one from the Split model is the same as the registration end
        # (and one day before group stage start).
        logger.info("Checking if calibration stage ended")
        now_date = timezone.now().date()
        calibration_end_with_puffer = Split.objects.get_current_split().calibration_stage_start + timedelta(days=2)
        has_ended = calibration_end_with_puffer <= now_date
        logger.info(
            f"Calibration stage end with puffer: {calibration_end_with_puffer} --- "
            f"Current date: {now_date} --- "
            f"Calibration stage ended: {has_ended}"
        )
        return has_ended

    def cron(self) -> str:
        return "*/2 * * * *"

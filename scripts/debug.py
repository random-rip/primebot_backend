import logging

from app_prime_league.models import Team
from communication_interfaces.telegram_interface.tg_singleton import send_message
from utils.constants import EMOJI_GIFT, EMOJI_FIRE, EMOJI_TROPHY
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    logger = logging.getLogger("notifications_logger")
    logger.info(f"Start Sending Weekly Notifications...")
    teams = Team.objects.get_watched_teams()
    message = \
        """
        Hallo {},
        """ \
        f"""
die Gruppenphase des aktuellen PrimeLeague-Splits ist jetzt vorbei und wir hoffen, ihr habt das erreicht, was ihr erreichen wolltet. {EMOJI_TROPHY}
        
Natürlich wird euch der Primebot bei der Organisierung im kommenden Split weiterhin unterstützen. {EMOJI_GIFT}

Wir freuen uns, wenn ihr uns Feedback in [diesem PL Forenpost](https://www.primeleague.gg/de/forums/1418-league-of-legends/1469-off-topic/637268-pl-spieltag-updates-als-push-benachrichtigung-aufs-handy) gebt und würden uns wünschen, dass ihr den PrimeBot anderen Teams präsentiert (vielleicht seid ihr ja in einer Organisation oder einem Verein {EMOJI_FIRE}).  
        
Sternige Grüße
@Grayknife und @OrbisK
        """
    for team in teams:
        print(team)
        logger.debug(f"Sending Notification to {team}...")
        send_message(message.format(team.name), chat_id=team.telegram_id)


def run():
    main()

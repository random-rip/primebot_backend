import logging

from app_prime_league.models import Team
from communication_interfaces.telegram_interface.tg_singleton import send_message
from utils.constants import EMOJI_GIFT, EMOJI_FIRE, EMOJI_TROPHY
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    teams = Team.objects.get_watched_teams()
    message = \
        """
        Hallo {},
        """ \
        f"""
       
Sternige Grüße
@Grayknife und @OrbisK
        """
    for team in teams:
        print(team)
        send_message(message.format(team.name), chat_id=team.telegram_id)


def run():
    main()

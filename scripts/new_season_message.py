from app_prime_league.models import Team
from communication_interfaces import send_message
from communication_interfaces.languages.de_DE import GENERAL_MATCH_LINK
from utils.constants import EMOJI_ARROW


def main():
    teams = Team.objects.get_watched_team_of_current_split()
    for team in teams:
        next_match = team.games_against.order_by("game_day").first()
        pattern = f"\*Das nächste Match ist natürlich gegen " \
                  f"{EMOJI_ARROW}[{next_match.enemy_team.name}]({GENERAL_MATCH_LINK}{next_match.game_id}). 😇"

        send_message(msg=pattern, chat_id=team.telegram_id)


def run():
    main()

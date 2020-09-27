from app_prime_league.models import Team
from telegram_interface import send_message
from telegram_interface.messages import GENERAL_MATCH_LINK
from utils.constants import EMOJI_ONE, EMOJI_MINDBLOWN, EMOJI_SOON, EMOJI_ARROW, EMOJI_CLOVER, EMOJI_FIGHT


def main():
    # teams = Team.objects.exclude(telegram_id__isnull=True, division__isnull=True, id=89678)
    teams = Team.objects.filter(id__in=[93008, 101916, 111914, 119671])
    for team in teams:
        print(team)
        next_match = team.games_against.order_by("game_begin").first()
        pattern = "Hallo Beschwörer, \n \n" \
                  "der Wintersplit 2020 ❄ beginnt morgen und ich bin natürlich auch am Stizzle. \n" \
                  f"In diesem Chat wurde folgendes Team registriert: {team.name} \n" \
                  f"Ihr spielt in der Division {team.division} und euer nächstes " \
                  f"Match {EMOJI_SOON} bestreitet ihr gegen {EMOJI_ARROW}[{next_match.enemy_team.name}]({GENERAL_MATCH_LINK}{next_match.game_id}). \n\n" \
                  "*Hinweis:* \n" \
                  "Wenn es für dieses Team inzwischen eine neue Chatgruppe gibt, " \
                  "könnt ihr dieses mit /reassign in der neuen Gruppe initialisieren. \n\n" \
                  "*Coming Soon:* \n" \
                  f"{EMOJI_ONE} Discord-Bot Integration {EMOJI_MINDBLOWN}\n\n" \
                  f"Viel Erfolg auf den Richtfeldern! {EMOJI_FIGHT}\n" \
                  "Sternige Grüße \n" \
                  "@Grayknife _und_ @OrbisK"

        print(send_message(msg=pattern, chat_id=team.telegram_id))


def run():
    main()

from app_prime_league.models import Team
from communication_interfaces.languages.de_DE import GENERAL_MATCH_LINK
from communication_interfaces.message_dispatcher import MessageDispatcher
from utils.constants import EMOJI_ARROW_RIGHT, EMOJI_FIGHT, EMOJI_FIRE


def main():
    text = """
    _... a little upsi happened_
Hallo **{team.name}**, 
die Gruppenphase startet in ein paar Tagen und ihr spielt diesen Split in Division **{team.division}**. 

**Eine Übersicht eurer Spiele:**

"""
    ende = """

{emoji} GL & HF {emoji}
"""
    teams = Team.objects.get_watched_team_of_current_split()
    teams = teams.filter(
        id__in=[89678, 111914, 114430, 119395, 116152, 135184, 135572, 136932, 137796, 146630, 147718, 153698])
    for team in teams:
        print(team)
        try:
            games_to_play = team.games_against.filter(game_closed=False).order_by("game_day")
            a = [
                f"[Spieltag {game.game_day}]({GENERAL_MATCH_LINK}{game.game_id}) {EMOJI_FIGHT} {game.enemy_team.name} {EMOJI_ARROW_RIGHT} [OP.gg]({game.get_op_link_of_enemies(only_lineup=False)})\n"
                for game in games_to_play]
            games_text = "\n".join(a)
            dispatcher = MessageDispatcher(team)
            msg = text.format(team=team) + games_text + ende.format(emoji=EMOJI_FIRE)
            dispatcher.dispatch_raw_message(msg=msg)
        except Exception as e:
            print("ERROR", e)


# Command to run this file:
# python manage.py runscript debug
def run():
    main()

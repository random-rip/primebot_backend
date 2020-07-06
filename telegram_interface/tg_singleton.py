import telepot
from babel import dates as babel
from app_prime_league.models import Team, Game
from prime_league_bot import settings
from utils.constants import EMOJI_THREE, EMOJI_ONE, EMOJI_TWO, EMOJI_SUCCESS, EMOJI_ARROW

emoji_numbers = [
    EMOJI_ONE,
    EMOJI_TWO,
    EMOJI_THREE,
]
bot = telepot.Bot(token=settings.TELEGRAM_BOT_KEY)


def send_message(msg: str, chat_id: int = None):
    """
    Sends a Message using Markdown. If settings.DEBUG is True, overwrites the chat_id.
    """
    if settings.DEBUG or chat_id is None:
        chat_id = settings.DEFAULT_TELEGRAM_CHAT_ID
    bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="Markdown", disable_web_page_preview=True)


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class TelegramMessagesWrapper:

    @staticmethod
    def send_new_suggestion_of_enemies(game: Game):
        details = list(game.suggestion_set.all().values_list("game_begin", flat=True))
        prefix = f"{'Neuer Zeitvorschlag' if len(details) == 1 else 'Neue Zeitvorschläge'} von " \
                 f"{game.enemy_team.team_tag} für Spieltag {game.game_day}:\n"

        times = [format_datetime(x) for x in details]
        for i, val in enumerate(times):
            times[i] = f"{emoji_numbers[i]}{val}"
        text = prefix + "\n".join([format_datetime(x) for x in details])

        text += "\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{}) zur Seite.".format(
            game.game_id)
        send_message(msg=text, chat_id=game.team.telegram_channel_id)
        return

    @staticmethod
    def send_new_suggestion(game: Game):
        msg = f"Neuer [Zeitvorschlag von uns](https://www.primeleague.gg/de/leagues/matches/{game.game_id}) " \
              f"für Spieltag {game.game_day} gegen {game.enemy_team.team_tag}. {EMOJI_SUCCESS}"
        send_message(msg=msg, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_scheduling_confirmation(game: Game, auto_confirm):
        time = format_datetime(game.game_begin)
        if auto_confirm:
            text = f"Das Team {game.enemy_team.team_tag} hat für Spieltag {game.game_day} weder die vorgeschlagene " \
                   f"Zeit angenommen, noch eine andere vorgeschlagen. Damit ist der Spieltermin\n{EMOJI_ARROW}" + \
                   f"{time} bestätigt."

        else:
            text = f"Spielbestätigung von {game.enemy_team.team_tag} für Spieltag {game.game_day}:\n{EMOJI_ARROW}" \
                   f"{time}"

        text += f"\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{game.game_id}) zur Seite."
        send_message(msg=text, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_new_lineup_of_enemies(game: Game, ):
        op_link = game.get_op_link_of_enemies(only_lineup=True)
        if op_link is None:
            raise Exception()
        text = f"{game.enemy_team.team_tag} hat ein neues [Lineup]({op_link}) aufgestellt."
        send_message(msg=text, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_new_game_day(game: Game):
        op_link = game.get_op_link_of_enemies(only_lineup=False)
        text = f"Spieltag {game.game_day} gegen [{game.enemy_team.team_tag}]" \
               f"(https://www.primeleague.gg/de/leagues/matches/{game.game_id}):" \
               f"\nHier ist der [op.gg-Link]({op_link}) des Teams."
        send_message(msg=text, chat_id=game.team.telegram_channel_id)

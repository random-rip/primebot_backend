from typing import List

from telegram import Chat, Message, Update

from app_prime_league.models import Player, Team
from bots.telegram_interface.commands.single_commands import call_match


class TestBot:
    response_text: str = ''

    def send_message(self, chat_id, *args, **kwargs):
        self.response_text = args[0] if args else kwargs.get("text", "")

        return None


class TestChat(Chat):
    type = Chat.CHANNEL


def test_call_match(text: str, chat, bot) -> str:
    message = Message(1, 1, None, chat, text=text, bot=bot)
    update = Update(1, message)

    call_match(update, None)


def create_team_with_player_names(team_name: str, player_names: List[str], *, telegram_id: int = None) -> Team:
    team = Team.objects.create(name=team_name, telegram_id=telegram_id)
    for player_name in player_names:
        Player.objects.create(name=player_name, team=team)

    return team

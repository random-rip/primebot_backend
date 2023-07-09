from django.utils.datetime_safe import datetime
from telegram import Chat, Message, Update

from app_prime_league.models import Player, Team, Match
from bots.telegram_interface.commands.single_commands import call_match


class TestBot:
    response_text: str = ''

    def send_message(self, chat_id, *args, **kwargs):
        self.response_text = args[0] if args else kwargs.get("text", "")


class TestChat(Chat):
    type = Chat.CHANNEL


def test_call_match(text: str, chat, bot):
    message = Message(1, 1, None, chat, text=text, bot=bot)
    update = Update(1, message)

    call_match(update, None)


class TeamBuilder:
    def __init__(self, team_name: str):
        self.team_name = team_name
        self.players = []
        self.language = Team.Languages.GERMAN
        self.telegram_id = None

    def add_players_by_names(self, *player_names):
        for player_name in player_names:
            self.players.append(Player(name=player_name))
        return self

    def set_language(self, language: Team.Languages):
        self.language = language
        return self

    def set_telegram_id(self, telegram_id: int):
        self.telegram_id = telegram_id
        return self

    def build(self):
        team = Team.objects.create(name=self.team_name, telegram_id=self.telegram_id, language=self.language)
        for player in self.players:
            player.team = team

        return team


class MatchBuilder:
    def __init__(self, match_id: int, team_1: Team, team_2: Team):
        self.match_id = match_id
        self.team_1 = team_1
        self.team_2 = team_2
        self.match_day = 2
        self.has_side_choice = False
        self.match_type = Match.MATCH_TYPE_LEAGUE
        self.begin = None

    def set_match_day(self, match_day: int):
        self.match_day = match_day
        return self

    def does_have_side_choice(self):
        self.has_side_choice = True
        return self

    def set_match_type(self, match_type: str):
        self.match_type = match_type
        return self

    def begin_at(self, begin: datetime):
        self.begin = begin
        return self

    def build(self):
        Match.objects.create(
            match_id=self.match_id,
            team=self.team_1,
            enemy_team=self.team_2,
            match_day=self.match_day,
            has_side_choice=self.has_side_choice,
            match_type=Match.MATCH_TYPE_LEAGUE,
            begin=self.begin
        )

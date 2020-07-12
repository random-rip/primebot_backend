import concurrent.futures
import time

from django.db.models import Q

from app_prime_league.models import Team, Player, Game, GameMetaData
from parsing.parser import TeamHTMLParser, TeamWrapper


def register_team(team_id, tg_group_id):
    team = add_team(team_id, tg_group_id)
    if team is not None:
        try:
            wrapper = TeamWrapper(team_id=team.id)
        except Exception:
            return None
        add_players(wrapper.parser, team)
        add_games(wrapper.parser, team)
        return team
    else:
        return None


def add_team(team_id, tg_group_id):
    if Team.objects.filter(
            Q(id=team_id, telegram_channel_id__isnull=False) |
            Q(telegram_channel_id=tg_group_id)).exists():
        print("Dieser Telegramgruppe ist bereits ein Team zugewiesen.")
        return None

    try:
        wrapper = TeamWrapper(team_id=team_id)
        parser = wrapper.parser
    except Exception:
        print("Wrapper is None")
        return None

    team, created = Team.objects.get_or_create(id=team_id, defaults={
        "name": parser.get_team_name(),
        "team_tag": parser.get_team_tag(),
        "division": parser.get_current_division(),
        "telegram_channel_id": tg_group_id,
    })
    if not created:
        team.telegram_channel_id = tg_group_id
        team.save()
    return team


def update_team(tg_chat_id, settings: dict):
    try:
        team = Team.objects.get(telegram_channel_id=tg_chat_id)
    except Team.DoesNotExist:
        print("Team existiert nicht")
        return None
    for key, value in settings.items():
        setting, _ = team.setting_set.get_or_create(attr_name=key, defaults={
            "attr_value": value,
        })
        setting.attr_value = value
        setting.save()
    return team


def add_players(parser: TeamHTMLParser, team: Team):
    members = parser.get_members()
    for (id_, name, summoner_name, is_leader,) in members:
        player, created = Player.objects.get_or_create(id=id_, defaults={
            "name": name,
            "team": team,
            "summoner_name": summoner_name,
            "is_leader": is_leader,
        })
        if not created:
            player.is_leader = is_leader
            player.summoner_name = summoner_name
            player.save()


def add_game(team, game_id):
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    game = Game.objects.get_game_by_team(game_id=game_id, team=team)
    if game is None:
        game = Game()
    else:
        print("Spiel existiert bereits in der Datenbank und wird geupdated")
    gmd.get_enemy_team_data()
    game.update_from_gmd(gmd)
    game.update_enemy_team(gmd)
    game.update_enemy_lineup(gmd)
    game.update_latest_suggestion(gmd)


def add_games(parser: TeamHTMLParser, team: Team):
    start_time = time.time()
    game_ids = parser.get_matches()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda p: add_game(*p), ((team, game_id) for game_id in game_ids))
    duration = time.time() - start_time
    print(f"Added games ({len(game_ids)}) in {duration} seconds")

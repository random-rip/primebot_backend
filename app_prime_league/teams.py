import time

from app_prime_league.models import Team, Player, Game, GameMetaData
from parsing.parser import TeamHTMLParser, TeamWrapper


def register_team(team_id, tg_group_id):
    team = add_team(team_id, tg_group_id)
    if team is not None:
        parser = TeamWrapper(team_id=team.id).parser
        add_players(parser, team)
        add_games(parser, team)


def add_team(team_id, tg_group_id):
    wrapper = TeamWrapper(team_id=team_id)
    if wrapper is None:
        print("Dieses Team wurde nicht gefunden")
        return
    parser = wrapper.parser

    if Team.objects.filter(id=team_id, telegram_channel_id__isnull=False).exists():
        print("Das Team existiert bereits und eine Telegram Chat ID ist schon hinterlegt")
        return None
    team, created = Team.objects.get_or_create(id=team_id, defaults={
        "name": parser.get_team_name(),
        "team_tag": parser.get_team_tag(),
        "division": parser.get_current_division(),
        "telegram_channel_id": tg_group_id,
    })
    return team


def update_team(team_id, settings: dict):
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        print("Team existiert nicht")
        return
    # TODO Sachen updaten


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


def add_games(parser: TeamHTMLParser, team: Team):
    start_time = time.time()
    game_ids = parser.get_matches()
    for j in game_ids:
        gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=j,)
        game = Game.objects.get_game_by_team(game_id=j, team=team)
        if game is None:
            game = Game()
        else:
            print("Spiel existiert bereits in der Datenbank und wird geupdated")
        gmd.get_enemy_team_data()
        game.update_from_gmd(gmd)
        game.update_enemy_team(gmd)
        game.update_enemy_lineup(gmd)
        game.update_latest_suggestion(gmd)
    duration = time.time() - start_time
    print(f"Added games ({len(game_ids)}) in {duration} seconds")

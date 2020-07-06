from app_prime_league.models import Team, Player, Game, GameMetaData
from data_crawling.api import crawler
from parsing.regex_operations import TeamHTMLParser


def apply_team(team_id):
    team = add_team(team_id)
    parser = TeamHTMLParser(crawler.get_team_website(team.id))
    add_players(parser, team)
    add_games(parser(), team)


def add_team(team_id):
    team, created = Team.objects.get_or_create(id=team_id)
    if not created and team.telegram_channel_id is not None:
        print("Team existiert bereits")
        return None
    return team


def add_players(parser: TeamHTMLParser, team: Team):
    members = parser.get_members()
    for (id_, name, summoner_name, is_leader,) in members:
        print(id_, name, summoner_name, is_leader,)
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
    game_ids = parser.get_matches()

    for j in game_ids:
        if Game.objects.get_game_by_team(game_id=j, team=team) is None:
            website = crawler.get_match_website(j)
            gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=j, website=website)
            Game().update_from_gmd(gmd)
        else:
            print("Spiel existiert bereits in der Datenbank")

from app_prime_league.models import Team, Game, Player
from comparing.game_comparer import GameMetaData
from data_crawling.api import Crawler
from parsing.regex_operations import TeamHTMLParser
from telegram import send_message


def main():
    crawler = Crawler(local=True)
    teams = Team.objects.get_watched_teams()
    # TODO add Players to DB
    for i in teams:
        parser = TeamHTMLParser(crawler.get_team_website(i.id))
        match_ids = parser.get_matches()
        for j in match_ids:
            website = crawler.get_match_website(j)
            gmd = GameMetaData.create_game_meta_data_from_website(team=i, game_id=j, website=website)
            # Game().save_or_update(gmd)

        members = parser.get_members()
        for (id_, name, summoner_name, is_leader,) in members:
            player, _ = Player.objects.get_or_create(id=id_, defaults={
                "name": name,
                "team":  i,
                "summoner_name": summoner_name,
                "is_leader": is_leader,
            })


def run():
    main()

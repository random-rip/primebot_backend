from app_prime_league.models import Team, Game
from comparing.game_comparer import GameMetaData
from data_crawling.api import Crawler
from parsing.regex_operations import TeamHTMLParser
from telegram import send_message


def main():
    crawler = Crawler(local=True)
    teams = Team.objects.get_watched_teams()
    # TODO add Players to DB
    for i in teams:
        match_ids = TeamHTMLParser(crawler.get_team_website(i.id)).get_matches()
        for j in match_ids:
            website = crawler.get_match_website(j)
            gmd = GameMetaData.create_game_meta_data_from_website(team=i, game_id=j, website=website)
            Game().save_or_update(gmd)

    send_message(chat_id=123, msg="test")


def run():
    main()

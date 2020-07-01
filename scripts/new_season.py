from app_prime_league.models import Team, Game
from comparing.game_comparer import GameMetaData
from data_crawling.api import Crawler
from parsing.regex_operations import HTMLParser


def main():
    crawler = Crawler(local=False)
    teams = Team.objects.get_watched_teams()
    # TODO add Players to DB
    for i in teams:
        match_ids = HTMLParser(crawler.get_team_website(i.id)).get_matches()
        for j in match_ids:
            website = crawler.get_match_website(j)
            gmd = GameMetaData.create_game_meta_data_from_website(team=i, game_id=j, website=website)
            Game().save_or_update(gmd)

    # bot = Bot(token=os.getenv("TELEGRAM_BOT_API_KEY"))
    # bot.sendMessage(chat_id=chat_id, text="Added Games for team {}".format(team_id), parse_mode="Markdown")


def run():
    main()

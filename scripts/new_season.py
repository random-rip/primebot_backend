from app_prime_league.models import Team
from data_crawling.api import Crawler
from parsing.managers import GameManager
from parsing.regex_operations import HTMLParser


# def main(team_id, chat_id):
    # ids = RegexOperator.get_matches(get_matches(team_id))
    # new_season(ids, chat_id, team_id)
    # bot = Bot(token=os.getenv("TELEGRAM_BOT_API_KEY"))
    # bot.sendMessage(chat_id=chat_id, text="Added Games for team {}".format(team_id), parse_mode="Markdown")


def new_season(ids, chat_id, team_id):
    for i in ids:
        website = get_website_of_match(i)
        game_day = HTMLParser.get_game_day(website)
        enemy_team_id = HTMLParser.get_enemy_team_id(website)
        game = Game(i, [], game_day,
                    enemy_team_id)
        dump = game.serialize()
        query = "INSERT INTO prime_leagues (id, json, game_closed, game_day, enemy_team_id, chat_id, team_id) VALUES ({},'{}',{}, {}, {}, {}, {})" \
            .format(i, dump, game.match_ended, game_day, enemy_team_id, chat_id, team_id)
        database.insert_to_db(query)


def run():
    crawler = Crawler(local=False)
    teams = Team.objects.get_watched_teams()

    for i in teams:
        match_ids = HTMLParser(crawler.get_matches_website(i)).get_matches()
        for j in match_ids:
            website = crawler.get_match_website(j)
            game = GameManager.create_game_from_website(team=i, game_id=j, website=website)
            game.save()

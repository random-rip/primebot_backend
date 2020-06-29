from api import get_website_of_match
from regex_operations import RegexOperator


def main():
    game_id = 597478
    website = get_website_of_match(game_id)
    game_day = RegexOperator.get_game_day(website)
    print("gameday " + game_day)
    logs = RegexOperator.get_logs(website)
    print(logs)
    sumNames = RegexOperator.get_summoner_names("91700")  # 596848
    # print(sumNames)
    print(RegexOperator.get_enemy_team_id("597508"))


if __name__ == '__main__':
    main()

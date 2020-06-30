from api import get_website_of_match, get_website_of_team
from regex_operations import RegexOperator


def main():
    game_id = 597478
    website = get_website_of_match(game_id)
    logs = RegexOperator.get_logs(website)
    sumNames = RegexOperator.get_summoner_names(get_website_of_team("91700"))
    # print(sumNames)
    print(RegexOperator.get_enemy_team_id(get_website_of_match("597508")))
    print(RegexOperator.get_summoner_names(get_website_of_team("91700")))


if __name__ == '__main__':
    main()

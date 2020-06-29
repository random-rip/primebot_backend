from app_prime_league.models import Team


def main():
    teams = Team.objects.all()

    for i in teams:
        game = database.get_next_uncompleted_game(i)
        if game == None:
            continue
        _id = game[0]
        chat_id = game[6]
        match_website = get_website_of_match(_id)

        game_day = RegexOperator.get_game_day(match_website)
        enemy_team_name = RegexOperator.get_enemy_team_name(match_website)
        new_game = Game(_id, RegexOperator.get_logs(match_website), RegexOperator.get_game_day(match_website),
                        RegexOperator.get_enemy_team_id(match_website))
        op_link = new_game.create_general_op_link_of_enemies()
        bot.sendMessage(chat_id=chat_id,
                        text="Spieltag {} gegen [{}](https://www.primeleague.gg/de/leagues/matches/{}):"
                             "\nHier ist der [op.gg-Link]({}) des Teams."
                        .format(game_day, enemy_team_name, _id, op_link), parse_mode="Markdown")


def _main():
    main()
    database.close_connection()


if __name__ == '__main__':
    _main()

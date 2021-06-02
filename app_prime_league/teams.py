import concurrent.futures
import logging
import sys
import traceback

from telegram import ParseMode

from app_prime_league.models import Team, Player, Game, GameMetaData
from communication_interfaces import send_message
from parsing.parser import TeamHTMLParser, TeamWrapper
from prime_league_bot import settings

logger = logging.getLogger("django")


def register_team(*, team_id, **kwargs):
    """
    Add or Update a Team, Add or Update Players, Add or Update Games. Optionally set telegram_id of the team.
    """
    team = add_or_update_team(team_id=team_id, **kwargs)
    if team is not None:
        try:
            wrapper = TeamWrapper(team_id=team.id)
        except Exception:
            return None
        if team.division is not None:
            try:
                add_or_update_players(wrapper.parser.get_members(), team)
                add_games(wrapper.parser.get_matches(), team)
            except Exception as e:
                trace = "".join(traceback.format_tb(sys.exc_info()[2]))
                send_message(
                    f"Ein Fehler ist beim Updaten von Team {team.id} {team.name} aufgetreten:\n<code>{trace}\n{e}</code>",
                    chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
                logger.error(e)

        return team
    else:
        return None


def reassign_team(team_id, tg_group_id):
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist as e:
        return None

    team.telegram_id = tg_group_id
    team.save()
    return team


def reassign_chat(team_id, tg_group_id):
    try:
        old_team = Team.objects.get(telegram_id=tg_group_id)
    except Team.DoesNotExist as e:
        return None

    old_team.telegram_id = None
    # TODO old team chat bescheid geben
    old_team.save()

    try:
        new_team = Team.objects.get(id=team_id)
        new_team.telegram_id = tg_group_id
        new_team.save()
    except Team.DoesNotExist as e:
        new_team = register_team(team_id=team_id, telegram_id=tg_group_id)

    return new_team


def add_or_update_team(*, team_id, **kwargs):
    try:
        wrapper = TeamWrapper(team_id=team_id)
        parser = wrapper.parser
    except Exception:
        print("Wrapper is None")
        return None

    defaults = {
        "name": parser.get_team_name(),
        "team_tag": parser.get_team_tag(),
        "division": parser.get_current_division(),
        "logo_url": parser.get_logo(),
    }
    defaults = {**defaults, **kwargs}

    team, created = Team.objects.get_or_create(id=team_id, defaults=defaults)
    if not created:
        Team.objects.filter(id=team.id).update(**kwargs)
        team = update_team(parser, team_id)
        team.save()
    return team


def update_team(parser: TeamHTMLParser, team_id: int):
    name = parser.get_team_name()
    logo = parser.get_logo()
    team_tag = parser.get_team_tag()
    division = parser.get_current_division()

    team = Team.objects.filter(id=team_id, name=name, logo_url=logo, team_tag=team_tag, division=division)
    if team.exists():
        return team.first()
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist as e:
        return None
    logger.debug(f"Updating {team}...")
    team.name = name
    team.logo_url = logo
    team.team_tag = team_tag
    team.division = division
    team.save()
    return team


def update_settings(tg_chat_id, settings: dict):
    try:
        team = Team.objects.get(telegram_id=tg_chat_id)
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


def add_or_update_players(members, team: Team):
    for (id_, name, summoner_name, is_leader,) in members:
        player = Player.objects.filter(id=id_, name=name, summoner_name=summoner_name, is_leader=is_leader).first()
        logger.debug(f"Updating {player}...")
        if player is not None:
            continue
        player, created = Player.objects.get_or_create(id=id_, defaults={
            "name": name,
            "team": team,
            "summoner_name": summoner_name,
            "is_leader": is_leader,
        })
        if not created:
            player.name = name
            player.is_leader = is_leader
            player.summoner_name = summoner_name
            player.save()


def add_game(team, game_id, ignore_lineup=False):
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    game = Game.objects.get_game_by_team(game_id=game_id, team=team)

    if game is None:
        game = Game()
    gmd.get_enemy_team_data()
    game.update_from_gmd(gmd)
    game.update_enemy_team(gmd)
    if not ignore_lineup:
        game.update_enemy_lineup(gmd)
    game.update_latest_suggestion(gmd)
    logger.debug(f"Updating {game}...")


def add_games(game_ids, team: Team, ignore_lineup=False, use_concurrency=True):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: add_game(*p), ((team, game_id, ignore_lineup) for game_id in game_ids))
    else:
        for i in game_ids:
            add_game(team, game_id=i)


def add_raw_game(team, game_id):
    Game.objects.get_or_create(
        game_id=game_id,
        team=team,
    )


def add_raw_games(game_ids, team: Team, use_concurrency=True):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: add_raw_game(*p), ((team, game_id) for game_id in game_ids))
        return
    else:
        for i in game_ids:
            add_raw_game(team, game_id=i)

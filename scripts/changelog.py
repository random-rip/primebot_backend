from app_prime_league.models import Team
from communication_interfaces import send_message
from communication_interfaces.message_dispatcher import MessageDispatcher
from utils.changelogs import CHANGELOGS


def main():
    log = CHANGELOGS[sorted(CHANGELOGS.keys())[-1]]
    pattern = log["text"]
    teams = Team.objects.get_watched_teams()
    for team in teams:
        dispatcher = MessageDispatcher(team)
        msg = pattern.format(team=team, version=log["version"])
        dispatcher.dispatch_raw_message(msg=msg)
        # if team.value_of_setting("changelog_update"):
        #     msg = pattern.format(team=team, version=log["version"])
        #     print(send_message(msg=msg, chat_id=team.telegram_id))

def run():
    main()

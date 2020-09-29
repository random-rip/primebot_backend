from app_prime_league.models import Team
from telegram_interface import send_message
from utils.changelogs import CHANGELOGS


def main():
    log = CHANGELOGS[sorted(CHANGELOGS.keys())[-1]]
    pattern = log["text"]
    # teams = Team.objects.exclude(telegram_id__isnull=True)
    teams = Team.objects.filter(id__in=[119413, 89678])
    for team in teams:
        if team.value_of_setting("changelog_update"):
            msg = pattern.format(team=team, version=log["version"])
            print(send_message(msg=msg, chat_id=team.telegram_id))


def run():
    main()

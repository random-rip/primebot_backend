from app_prime_league.models import Team
from telegram_interface import send_message


def main():
    pattern = "Hallo {team_tag},\n" \
              "hier ein kurzes Update der letzten größeren Änderungen am Bot.\n\n" \
              "*Neuer Command:* \n" \
              "- /setlogo - setzt euer Telegram Gruppenbild auf das bei der PrimeLeague hinterlegte Foto. "

    teams = Team.objects.exclude(telegram_id__isnull=True)
    for team in teams:
        print(team.id)
        # if team.id in [111914, 93008, 105959, 105878, ]:
        #     continue
        msg = pattern.format(team_tag=team.team_tag, )
        print(send_message(msg=msg, chat_id=team.telegram_id))


def run():
    main()

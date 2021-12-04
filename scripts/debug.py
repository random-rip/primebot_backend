from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher


def main():
    team = Team.objects.get(id=155398)
    dispatcher = MessageDispatcher(team)
    msg = "TEST"
    dispatcher.dispatch_raw_message(msg=msg)


# python manage.py runscript debug
def run():
    main()

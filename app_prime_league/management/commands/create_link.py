from django.core.management import BaseCommand

from app_prime_league.models import Team
from app_prime_league.modules.team_settings import SettingsMaker


class Command(BaseCommand):
    def handle(self, *args, **options):
        maker = SettingsMaker(team=Team.objects.first())
        link = maker.generate_expiring_link("discord")
        maker2 = SettingsMaker(data=link)
        print(maker2.link_is_valid())
        print(maker2.errors)

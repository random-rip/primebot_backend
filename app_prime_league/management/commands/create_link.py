from django.core.management import BaseCommand

from app_api.modules.team_settings.maker import SettingsMaker
from app_prime_league.models import Team


class Command(BaseCommand):
    def handle(self, *args, **options):
        maker = SettingsMaker(team=Team.objects.first())
        link = maker.generate_expiring_link("discord")
        print(link)

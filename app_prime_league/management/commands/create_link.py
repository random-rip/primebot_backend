from django.core.management import BaseCommand

from app_prime_league.models import Team
from core.settings_maker import SettingsMaker


class Command(BaseCommand):
    def handle(self, *args, **options):
        maker = SettingsMaker(team=Team.objects.first())
        link = maker.generate_expiring_link("discord")
        print(link)

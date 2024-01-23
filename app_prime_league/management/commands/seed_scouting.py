from django.conf import settings
from django.core.management import BaseCommand

from app_prime_league.models import ScoutingWebsite


class Command(BaseCommand):
    def handle(self, *args, **options):
        ScoutingWebsite.objects.all().delete()
        _ = ScoutingWebsite.objects.create(
            id=1,
            name=settings.DEFAULT_SCOUTING_NAME,
            base_url=settings.DEFAULT_SCOUTING_URL,
            separator=settings.DEFAULT_SCOUTING_SEP,
        )
        _ = ScoutingWebsite.objects.create(
            id=2, name="U.GG", base_url="https://u.gg/multisearch?summoners={}&region=euw1", separator=","
        )
        _ = ScoutingWebsite.objects.create(
            id=3, name="XDX.GG", base_url="https://xdx.gg/lol/multi/euw/{}", separator="-"
        )

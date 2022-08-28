from django.core.management import BaseCommand

from bots.discord_interface.discord_bot import DiscordBot


class Command(BaseCommand):
    def handle(self, *args, **options):
        DiscordBot().run()

from django.core.management import BaseCommand

from bots.telegram_interface.telegram_bot import TelegramBot


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Bot is listening...")
        TelegramBot().run()

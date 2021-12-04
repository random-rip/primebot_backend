from communication_interfaces.telegram_interface.telegram_bot import TelegramBot


# python manage.py runscript run_telegram_bot
def run():
    print("Bot is listening...")
    TelegramBot().run()

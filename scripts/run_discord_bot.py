from communication_interfaces.discord_interface.discord_bot import DiscordBot


# python manage.py runscript run_discord_bot
def run():
    print("Bot is listening...")
    DiscordBot().run()

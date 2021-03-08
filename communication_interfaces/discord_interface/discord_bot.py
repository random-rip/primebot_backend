from asgiref.sync import sync_to_async
from discord.ext import commands

from app_prime_league.models import Team
from app_prime_league.teams import register_team_discord
from communication_interfaces.base_bot import Bot
from prime_league_bot import settings


class DiscordBot(Bot):
    """
    DiscordBot Class. Provides Communication with Bot(Discord API) and Client
    """

    def __init__(self):
        super().__init__(
            bot=commands.Bot,
            bot_config={
                "token": settings.DISCORD_BOT_KEY,
                "command_prefix": '!'
            },
        )

    def _initialize(self):
        @self.bot.command(name='start', help='Team initialisieren', pass_context=True)
        async def start(ctx, team_id_or_url):
            chat_existing = await sync_to_async(Team.objects.filter(discord_channel_id=ctx.message.channel.id).exists)()
            team_existing = await sync_to_async(
                Team.objects.filter(id=team_id_or_url, discord_channel_id__isnull=False).exists)()

            if chat_existing:
                await ctx.send("Für diesen Channel ist bereits ein Team registriert!")
            elif team_existing:
                await ctx.send("Dieses Team ist bereits registriert!")
            else:
                team = await sync_to_async(
                    register_team_discord)(team_id=team_id_or_url, discord_id=ctx.message.channel.id)
                response = f"Channel {ctx.message.channel} wurde für Team {team.name} initialisiert!"
                await ctx.send(response)

    def run(self):
        self.bot.run(self.token)

    @staticmethod
    def send_message():
        # TODO implement Webhook here
        pass

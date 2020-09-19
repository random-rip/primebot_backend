import random

from asgiref.sync import sync_to_async
from discord.ext import commands

from app_prime_league.models import Team
from app_prime_league.teams import register_team_discord
from prime_league_bot import settings


class DiscordBot:
    """
    DiscordBot Class. Provides Communication with Bot(Discord API) and Client
    """

    def __init__(self):
        self.api_key = settings.DISCORD_BOT_KEY
        self.bot = commands.Bot(command_prefix='!')

    def run(self):
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

        self.bot.run(self.api_key)

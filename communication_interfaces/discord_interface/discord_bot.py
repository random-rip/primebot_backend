import base64
import os

from asgiref.sync import sync_to_async
from discord.ext import commands

from discord import Webhook, RequestsWebhookAdapter, Embed, Colour

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from communication_interfaces.base_bot import Bot
from communication_interfaces.languages.de_DE import WAIT_A_MOMENT_TEXT
from communication_interfaces.utils import mysql_has_gone_away
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
        @mysql_has_gone_away
        @self.bot.command(name='start', help='Team initialisieren', pass_context=True)
        async def start(ctx, team_id_or_url):
            channel = ctx.message.channel
            chat_existing = await sync_to_async(Team.objects.filter(discord_channel_id=channel.id).exists)()
            team_existing = await sync_to_async(
                Team.objects.filter(id=team_id_or_url, discord_webhook_id__isnull=False).exists)()

            if chat_existing:
                await ctx.send(
                    "Für diesen Channel ist bereits ein Team registriert! Solltet Ihr keine Nachrichten mehr bekommen, nutzt bitte !fix")
            elif team_existing:
                await ctx.send("Dieses Team ist bereits in einem anderen Channel registriert!")
            else:
                webhook = await _create_new_webhook(ctx)
                if webhook is not None:
                    await ctx.send(WAIT_A_MOMENT_TEXT)
                    team = await sync_to_async(
                        register_team)(team_id=team_id_or_url, discord_webhook_id=webhook.id,
                                       discord_webhook_token=webhook.token, discord_channel_id=channel.id)
                    response = f"Channel {ctx.message.channel} wurde für Team {team.name} initialisiert!"
                    await ctx.send(response)

        @mysql_has_gone_away
        @self.bot.command(name="fix", help="Erstellt den Webhook im Channel neu.", pass_context=True)
        async def fix(ctx):
            channel = ctx.message.channel
            team = await sync_to_async(Team.objects.filter(discord_channel_id=channel.id).first)()
            if team is not None:
                webhook = await _create_new_webhook(ctx)
                if webhook is None:
                    return
                team.discord_webhook_id = webhook.id
                team.discord_webhook_token = webhook.token
                await sync_to_async(team.save)()
                await ctx.send(
                    "Webhook wurde neu erstellt. Sollten weiterhin Probeleme auftreten wende dich bitte an den Support."
                )
            else:
                await ctx.send("In diesem Channel ist derzeitig kein Team registriert. Bitte nutze !start <team_id>")
                return

        async def _create_new_webhook(ctx):
            channel = ctx.message.channel
            webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
            for webhook in webhooks:
                await webhook.delete()
            with open(os.path.join(settings.BASE_DIR, "documents", "primebot_logo.jpg"), "rb") as image_file:
                avatar = image_file.read()
            webhook = await channel.create_webhook(name="PrimeBot", avatar=avatar)
            return webhook

    def run(self):
        self.bot.run(self.token)

    @staticmethod
    def send_message(*, msg: str, team, attach):
        webhook = Webhook.partial(team.discord_webhook_id, team.discord_webhook_token, adapter=RequestsWebhookAdapter())
        embed = Embed(description=msg, color=Colour.from_rgb(255, 255, 0))
        webhook.send(embed=embed)
        return

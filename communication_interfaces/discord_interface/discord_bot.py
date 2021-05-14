import os

from asgiref.sync import sync_to_async
from discord import Webhook, RequestsWebhookAdapter, Embed, Colour
from discord.ext import commands

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from communication_interfaces.base_bot import Bot
from communication_interfaces.languages.de_DE import WAIT_A_MOMENT_TEXT
from communication_interfaces.utils import mysql_has_gone_away
from prime_league_bot import settings
from utils.exceptions import CouldNotParseURLException
from utils.messages_logger import log_from_discord
from utils.utils import get_valid_team_id


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
        @self.bot.command(name='start', help='Registers new team (Format: !start <TEAM_ID oder TEAM_URL>)', pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def start(ctx, team_id_or_url):

            try:
                team_id = get_valid_team_id(team_id_or_url)
            except CouldNotParseURLException:
                await ctx.send(
                    "Aus dem Übergabeparameter konnte keine ID gefunden werden. (Format !start <TEAM_ID oder TEAM_URL>)")
                return

            channel = ctx.message.channel
            chat_existing = await sync_to_async(Team.objects.filter(discord_channel_id=channel.id).exists)()
            team_existing = await sync_to_async(
                Team.objects.filter(id=team_id, discord_webhook_id__isnull=False).exists)()

            if chat_existing:
                await ctx.send(
                    "Für diesen Channel ist bereits ein Team registriert! Solltet Ihr keine Nachrichten mehr bekommen, nutzt bitte !fix.")
                return
            if team_existing:
                await ctx.send("Dieses Team ist bereits in einem anderen Channel registriert!")
                return
            webhook = await _create_new_webhook(ctx)
            if webhook is not None:
                await ctx.send(WAIT_A_MOMENT_TEXT)
                team = await sync_to_async(
                    register_team)(team_id=team_id, discord_webhook_id=webhook.id,
                                   discord_webhook_token=webhook.token, discord_channel_id=channel.id)
                response = f"Channel {ctx.message.channel} wurde für Team {team.name} initialisiert!"
                await ctx.send(response)

        @self.bot.command(name="fix", help="Recreates the notifications webhook", pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
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
                    "Webhook wurde neu erstellt. Sollten weiterhin Probleme auftreten, wendet euch bitte an den Support."
                )
            else:
                await ctx.send("In diesem Channel ist derzeitig kein Team registriert. Benutzt dafür !start <TEAM_ID oder TEAM_URL>")
                return

        @self.bot.command(name="role", help="Set or unset role to mention it in notifications", pass_context=True)
        @commands.check(mysql_has_gone_away)
        async def set_role(ctx, role_name=None):
            # TODO: Check ob team initialisiert etc.
            if role_name is None:
                #TODO unset für Team
                return

            roles = ctx.message.author.guild.roles
            role = None
            for i in roles:
                if i.name == role_name:
                    role = i
                    break
            if role is None:
                # TODO Role not found on server
                return
            # TODO role.mention speichern
            await ctx.send(f"{role.mention} Yo hier du geiler Babo")
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
        embed = Embed(description=f"@Primeleague  Notifications {msg}", color=Colour.from_rgb(255, 255, 0))
        webhook.send(embed=embed)
        return

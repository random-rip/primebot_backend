import os
import re
from io import BytesIO

import aiohttp
import discord
import requests
from asgiref.sync import sync_to_async
from discord import Webhook, RequestsWebhookAdapter, Embed, Colour
from discord.ext import commands

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from communication_interfaces.base_bot import Bot
from communication_interfaces.languages import de_DE as LanguagePack
from communication_interfaces.utils import mysql_has_gone_away
from prime_league_bot import settings
from utils.exceptions import CouldNotParseURLException
from utils.messages_logger import log_from_discord
from utils.utils import get_valid_team_id

MENTION_PREFIX = "<@&"
MENTION_POSTFIX = ">"


class DiscordBot(Bot):
    """
    DiscordBot Class. Provides Communication with Bot(Discord API) and Client
    """

    def __init__(self):
        help_command = commands.DefaultHelpCommand(
            no_category='Commands'
        )

        super().__init__(
            bot=commands.Bot,
            bot_config={
                "token": settings.DISCORD_BOT_KEY,
                "command_prefix": '!',
                "description": LanguagePack.DC_DESCRIPTION,
                "help_command": help_command
            },
        )

    def _initialize(self):
        @self.bot.command(name='start', help=LanguagePack.DC_HELP_TEXT_START, pass_context=True, )
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def start(ctx, team_id_or_url=None):
            try:
                team_id = get_valid_team_id(team_id_or_url)
            except CouldNotParseURLException:
                await ctx.send(
                    LanguagePack.DC_TEAM_ID_NOT_VALID)
                return

            channel_id = ctx.message.channel.id
            if await get_registered_team_by_channel_id(channel_id=channel_id) is not None:
                await ctx.send(f"{LanguagePack.DC_CHANNEL_IN_USE} {LanguagePack.DC_USE_FIX}")
                return
            if await get_registered_team_by_team_id(team_id) is not None:
                await ctx.send(LanguagePack.DC_TEAM_IN_USE)
                return

            webhook = await _create_new_webhook(ctx)
            if webhook is None:
                await ctx.send(LanguagePack.DC_NO_PERMISSIONS_FOR_WEBHOOK)
                # TODO: hier gibt es noch keine Meldung an den User
                return
            await ctx.send(LanguagePack.WAIT_A_MOMENT_TEXT)
            async with ctx.typing():
                team = await sync_to_async(
                    register_team)(team_id=team_id, discord_webhook_id=webhook.id,
                                   discord_webhook_token=webhook.token, discord_channel_id=channel_id)
            response = LanguagePack.DC_REGISTRATION_FINISH.format(team_name=team.name)
            await ctx.send(response)

        @self.bot.command(name="fix", help=LanguagePack.DC_HELP_TEXT_FIX, pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def fix(ctx):
            channel = ctx.message.channel
            team = await get_registered_team_by_channel_id(channel_id=channel.id)
            if team is None:
                await ctx.send(LanguagePack.DC_CHANNEL_NOT_INITIALIZED)
                return
            async with ctx.typing():
                webhook = await _create_new_webhook(ctx)
                if webhook is None:
                    await ctx.send(LanguagePack.DC_NO_PERMISSIONS_FOR_WEBHOOK)
                    return
                team.discord_webhook_id = webhook.id
                team.discord_webhook_token = webhook.token
                await sync_to_async(team.save)()
            await ctx.send(LanguagePack.DC_WEBHOOK_RECREATED)

        @self.bot.command(name="role", help=LanguagePack.DC_HELP_TEXT_ROLE, pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def set_role(ctx, role_name=None):

            channel_id = ctx.message.channel.id
            team = await get_registered_team_by_channel_id(channel_id=channel_id)
            if team is None:
                await ctx.send(LanguagePack.DC_CHANNEL_NOT_INITIALIZED)
                return
            if role_name is None:
                team.discord_role_id = None
                await sync_to_async(team.save)()
                await ctx.send(LanguagePack.DC_ROLE_MENTION_REMOVED)
                return

            role = await parse_role(role_name, roles=ctx.message.author.guild.roles)
            if role is None:
                await ctx.send(LanguagePack.DC_ROLE_NOT_FOUND.format(role_name=role_name))
                return
            team.discord_role_id = role.id
            await sync_to_async(team.save)()
            await ctx.send(LanguagePack.DC_SET_ROLE.format(role_name=role.name))

        @self.bot.command(name="bop", help=LanguagePack.DC_HELP_TEXT_BOP, pass_context=True)
        @commands.check(log_from_discord)
        async def bop(ctx):
            contents = requests.get('https://dog.ceo/api/breeds/image/random').json()
            url = contents['message']
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        buffer = BytesIO(await resp.read())
            await ctx.send(file=discord.File(fp=buffer, filename="dog.jpg"))

        async def _create_new_webhook(ctx):
            channel = ctx.message.channel
            try:
                webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
                with open(os.path.join(settings.BASE_DIR, "documents", "primebot_logo.jpg"), "rb") as image_file:
                    avatar = image_file.read()
                webhook = await channel.create_webhook(name="PrimeBot", avatar=avatar)
                for webhook in webhooks:
                    await webhook.delete()
            except Exception as e:
                await log_from_discord(ctx, optional=f"{e}")
                return None
            return webhook

        async def get_registered_team_by_channel_id(channel_id):
            """

            :param channel_id: Integer
            :return: Instance of class Team or None
            """
            return await sync_to_async(Team.objects.filter(discord_channel_id=channel_id).first)()

        async def get_registered_team_by_team_id(team_id):
            """

            :param team_id: Integer
            :return: Instance of class Team or None
            """
            return await sync_to_async(Team.objects.filter(id=team_id, discord_webhook_id__isnull=False).first)()

        async def parse_role(value, roles):
            match = re.match(pattern=f"{MENTION_PREFIX}(?P<role_id>[0-9]*){MENTION_POSTFIX}", string=value)
            if match is not None:
                role_id = int(match.group('role_id'))
                for i in roles:
                    if i.id == role_id:
                        return i
            for i in roles:
                if i.name == value:
                    return i
            return None

    def run(self):
        self.bot.run(self.token)

    @staticmethod
    def send_message(*, msg: str, team, attach):
        webhook = Webhook.partial(team.discord_webhook_id, team.discord_webhook_token, adapter=RequestsWebhookAdapter())
        embed = Embed(description=msg, color=Colour.from_rgb(255, 255, 0))
        webhook.send(**DiscordBot.create_msg_arguments(discord_role_id=team.discord_role_id, embed=embed))

    @staticmethod
    def mask_mention(discord_role_id):
        if discord_role_id is None:
            return None
        return f"{MENTION_PREFIX}{discord_role_id}{MENTION_POSTFIX}"

    @staticmethod
    def mask_message_with_mention(*, discord_role_id, message: str):
        return f"{DiscordBot.mask_mention(discord_role_id)} {message}" if discord_role_id is not None else message

    @staticmethod
    def create_msg_arguments(*, discord_role_id, **kwargs):
        arguments = kwargs
        if discord_role_id is not None:
            arguments["content"] = DiscordBot.mask_mention(discord_role_id)
        return arguments

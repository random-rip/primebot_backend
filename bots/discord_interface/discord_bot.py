import logging

import discord
from discord import NotFound, Message
from discord.ext import commands
from discord.ext.commands import errors, NoPrivateMessage
from django.conf import settings
from django.utils.translation import gettext as _

from bots.base.bot_interface import BotInterface
from bots.discord_interface.utils import ChannelNotInUse, DiscordHelper
from bots.messages.base import BaseMessage
from utils.exceptions import VariableNotSetException
from utils.messages_logger import log_from_discord

logger = logging.getLogger("discord")
notifications_logger = logging.getLogger("notifications")
commands_logger = logging.getLogger("commands")


class DiscordBot(BotInterface):
    """
    DiscordBot Class. Provides Communication with Bot(Discord API) and Client
    """

    def __init__(self):
        if not settings.DISCORD_BOT_KEY:
            raise VariableNotSetException("DISCORD_BOT_KEY")
        if not settings.DISCORD_APP_CLIENT_ID:
            raise VariableNotSetException("DISCORD_APP_CLIENT_ID")
        super().__init__(bot=_DiscordBotV2, )

    def _initialize(self):
        self.bot.remove_command("help")

    def run(self):
        self.bot.run(settings.DISCORD_BOT_KEY)

    @staticmethod
    def send_message(*, msg: BaseMessage, team):
        webhook = discord.SyncWebhook.partial(
            id=team.discord_webhook_id,
            token=team.discord_webhook_token,
        )
        try:
            webhook.send(**DiscordHelper.create_msg_arguments(discord_role_id=team.discord_role_id, msg=msg))
        except NotFound as e:
            team.set_discord_null()
            notifications_logger.info(f"Could not send message to {team}: {e}. Soft deleted'")
        except Exception as e:
            notifications_logger.exception(f"Could not send message to {team}: '{msg}. -> {e}'")


class _DiscordBotV2(commands.Bot):
    """
    discord.py v2.0 bot class
    """

    def __init__(self, ):
        ext_directory = "ext"
        self.initial_extensions = [f".{ext_directory}.{x}" for x in [
            "bop",
            "start",
            "fix",
            "delete",
            "team_settings",
            "matches",
            "help",
        ]]
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default(),
        )

    async def on_ready(self):
        logger.info(f"{self.user} has connected to Discord!")

    async def on_command_error(self, ctx, exception: errors.CommandError, /):

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        exception = getattr(exception, 'original', exception)

        if isinstance(exception, ChannelNotInUse):
            await ctx.send(
                _("There is currently no team registered in this channel. Use `/start` to register a team."))
            return
        elif isinstance(exception, NoPrivateMessage):
            await ctx.send(_("This is a channel command."))
            return
        commands_logger.exception(exception)
        return await ctx.send(_(
            "An unknown error has occurred. Please contact the developers on Discord at {discord_link}."
        ).format(discord_link=settings.DISCORD_SERVER_LINK), suppress_embeds=True)

    async def setup_hook(self):
        logger.info("Hook setup...")
        await self.load_extensions()
        # await self.sync_commands()
        logger.info("Hooked setup.")

    async def on_message(self, message: Message, /):
        if message.interaction is not None:
            await log_from_discord(message)

    async def load_extensions(self):
        logger.info("Loading commands...")
        for ext in self.initial_extensions:
            await self.load_extension(name=ext, package="bots.discord_interface")
        logger.info("Commands loaded.")

    async def sync_commands(self):
        logger.info(f"Syncing commands: {[x.name for x in self.tree.get_commands()]} ...")
        if settings.DEBUG:
            guild = discord.Object(id=settings.DISCORD_GUILD_ID)
            logger.info(f"Debug is true, so commands will be synced to guild {guild}...")
            self.tree.copy_global_to(guild=guild)
            synced_commands = await self.tree.sync(guild=guild)
        else:
            logger.info(f"Debug is false, so commands will be synced globally. This can take up to an hour...")
            synced_commands = await self.tree.sync()
        logger.info(f"Synced commands: {[x.name for x in synced_commands]}")

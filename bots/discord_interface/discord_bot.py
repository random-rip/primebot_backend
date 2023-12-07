import logging

from asgiref.sync import sync_to_async
from discord import Intents, Message, NotFound, Object, SyncWebhook
from discord.ext.commands import Bot, NoPrivateMessage, errors
from django.conf import settings
from django.utils.translation import gettext as _

from bots.base.bot_interface import BotInterface
from bots.discord_interface.utils import ChannelNotInUse, DiscordHelper, translation_override
from bots.messages.base import BaseMessage
from utils.exceptions import VariableNotSetException
from utils.messages_logger import log_from_discord

discord_logger = logging.getLogger("discord")
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
        super().__init__(
            bot=_DiscordBotV2,
        )

    def _initialize(self):
        self.bot.remove_command("help")

    def run(self):
        self.bot.run(settings.DISCORD_BOT_KEY)

    @staticmethod
    def send_message(*, msg: BaseMessage, team):
        """
        This method is designed to send non-interactive messages. This is usually triggered by prime league updates.
        To send a message from a user triggered action (f.e. a reply message), use context based messages
        directly. This is different for each of the communication platforms.
        """
        webhook = SyncWebhook.partial(
            id=team.discord_webhook_id,
            token=team.discord_webhook_token,
        )
        try:
            webhook.send(**DiscordHelper.create_msg_arguments(discord_role_id=team.discord_role_id, msg=msg))
        except NotFound:
            team.set_discord_null()
            notifications_logger.info(f"Soft deleted Discord {team}'")
        except Exception as e:
            notifications_logger.exception(f"Could not send Discord Message {msg.__class__.__name__} to {team}", e)
            raise e


class _DiscordBotV2(Bot):
    """
    discord.py v2.0 bot class
    """

    def __init__(
        self,
    ):
        ext_directory = "ext"
        self.initial_extensions = [
            f".{ext_directory}.{x}"
            for x in [
                "bop",
                "start",
                "fix",
                "delete",
                "team_settings",
                "matches",
                "help",
            ]
        ]
        super().__init__(
            command_prefix="!",
            intents=Intents.default(),
        )

    async def on_ready(self):
        discord_logger.info(f"{self.user} has connected to Discord!")
        await self.change_presence(activity=None)
        # await self.change_presence(activity=Game(name='Maintenance Work'))

    @translation_override
    async def on_command_error(self, ctx, exception: errors.CommandError, /):
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        exception = getattr(exception, 'original', exception)

        if isinstance(exception, ChannelNotInUse):
            return await ctx.send(
                _("There is currently no team registered in this channel. Use `/start` to register a team.")
            )
        elif isinstance(exception, NoPrivateMessage):
            return await ctx.send(_("This is a channel command."))
        discord_logger.exception(exception, exc_info=True)
        return await ctx.send(
            _("An unknown error has occurred. Please contact the developers on Discord at {discord_link}.").format(
                discord_link=settings.DISCORD_SERVER_LINK
            ),
            suppress_embeds=True,
        )

    async def setup_hook(self):
        discord_logger.info("Hook setup...")
        await self.load_extensions()
        discord_logger.info("Hooked setup.")
        # await self.sync_commands()

    async def on_message(self, message: Message, /):
        pass

    async def on_interaction(self, interaction):
        await log_from_discord(interaction)

    async def on_app_command_completion(self, interaction, command):
        pass

    async def on_guild_channel_delete(self, channel):
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel.id)
        if team is None:
            return
        await sync_to_async(team.set_discord_null)()
        discord_logger.info(f"Set Discord to null for team {team} for channel {channel.name}.")

    async def load_extensions(self):
        discord_logger.info("Loading commands...")
        for ext in self.initial_extensions:
            await self.load_extension(name=ext, package="bots.discord_interface")
        discord_logger.info("Commands loaded.")

    async def sync_commands(self):
        discord_logger.info(f"Syncing commands: {[x.name for x in self.tree.get_commands()]} ...")
        if settings.DEBUG:
            guild = Object(id=settings.DISCORD_GUILD_ID)
            discord_logger.info(f"Debug is true, so commands will be synced to guild {guild.id}...")
            self.tree.copy_global_to(guild=guild)
            synced_commands = self.tree.get_commands(guild=guild)
        else:
            discord_logger.info("Debug is false, so commands will be synced globally. This can take up to an hour...")
            synced_commands = await self.tree.sync()
        discord_logger.info(f"Synced commands: {[x.name for x in synced_commands]}")

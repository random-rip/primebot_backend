import functools
import os
from typing import Callable, Union

from asgiref.sync import sync_to_async
from discord import Colour, Embed, Forbidden, Interaction, Webhook
from discord.ext import commands
from discord.ext.commands import Context
from django.conf import settings
from django.utils import translation

from app_prime_league.models import Team
from bots.messages.base import BaseMessage, MessageNotImplementedError
from utils.messages_logger import log_from_discord

MENTION_PREFIX = "<@&"
MENTION_POSTFIX = ">"

COLOR_NOTIFICATION = Colour.gold()
COLOR_SETTINGS = Colour.greyple()


class ChannelInUse(commands.CheckFailure):
    pass


class TeamInUse(commands.CommandError):
    pass


class NoWebhookPermissions(commands.CommandError):
    pass


class ChannelNotInUse(commands.CheckFailure):
    pass


class DiscordHelper:
    @staticmethod
    def create_msg_arguments(*, msg: BaseMessage, discord_role_id, color=COLOR_NOTIFICATION, **kwargs):
        arguments = kwargs
        try:
            arguments["embed"] = msg.generate_discord_embed()
        except MessageNotImplementedError:
            arguments["embed"] = Embed(description=msg.generate_message(), color=color)
        try:
            arguments["poll"] = msg.generate_poll()
        except MessageNotImplementedError:
            pass
        arguments["content"] = DiscordHelper.mask_message_with_mention(
            discord_role_id=discord_role_id, message=msg.generate_title()
        )
        return arguments

    @staticmethod
    def discord_role_pattern():
        return f"{MENTION_PREFIX}(?P<role_id>[0-9]*){MENTION_POSTFIX}"

    @staticmethod
    def mask_mention(discord_role_id):
        if discord_role_id is None:
            return None
        return f"{MENTION_PREFIX}{discord_role_id}{MENTION_POSTFIX}"

    @staticmethod
    def mask_message_with_mention(*, discord_role_id, message: str = ""):
        return f"{DiscordHelper.mask_mention(discord_role_id)} {message}" if discord_role_id is not None else message

    @staticmethod
    async def create_new_webhook(ctx) -> Webhook:
        """
        Raises:
            NoWebhookPermissions
        """
        channel = ctx.message.channel
        try:
            webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
            with open(os.path.join(settings.BASE_DIR, "documents", "primebot_logo.jpg"), "rb") as image_file:
                avatar = image_file.read()
            new_webhook = await channel.create_webhook(name="PrimeBot", avatar=avatar)
            for webhook in webhooks:
                await webhook.delete()
        except (Forbidden, Exception) as e:
            await log_from_discord(ctx.interaction, optional=f"{e}")
            raise NoWebhookPermissions
        return new_webhook

    @staticmethod
    async def get_registered_team_by_channel_id(channel_id: int) -> Union[None, Team]:
        return await sync_to_async(Team.objects.filter(discord_channel_id=channel_id).first)()

    @staticmethod
    async def get_registered_team_by_team_id(team_id: int) -> Union[None, Team]:
        return await sync_to_async(Team.objects.filter(id=team_id, discord_webhook_id__isnull=False).first)()


def check_channel_in_use() -> Callable:
    """
    Use this as a decorator.
    """

    async def predicate(ctx):
        channel_id = ctx.message.channel.id
        if await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel_id) is None:
            raise ChannelNotInUse
        return True

    return commands.check(predicate)


def check_channel_not_in_use() -> Callable:
    """
    Use this as a decorator.
    """

    async def predicate(ctx):
        channel_id = ctx.message.channel.id
        if await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel_id) is not None:
            raise ChannelInUse
        return True

    return commands.check(predicate)


async def check_team_not_registered(team_id: int) -> bool:
    """
    Cannot be used as a decorator
    """
    if await DiscordHelper.get_registered_team_by_team_id(team_id) is not None:
        raise TeamInUse
    return True


async def detect_language(interaction: Interaction) -> str:
    """
    Returns the language code from team, and if not registered from ``user.locale``.
    Returns: Language code
    """
    team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=interaction.channel_id)
    if team is not None:
        return team.language
    return str(interaction.locale)


def translation_override(func):
    """
    Decorator to enable and disable translation. The language is set based on the passed ``Context``. If no context
    is present, the default language from settings will be used.
    """

    @functools.wraps(func)
    async def wrapper_decorator(*args, **kwargs):
        for arg in args:
            if type(arg) == Context:
                context = arg
                break
        else:
            context = None
        language = await detect_language(context.interaction) if context is not None else settings.LANGUAGE_CODE
        translation.activate(language)
        try:
            value = await func(*args, **kwargs)
        finally:
            translation.deactivate()
        return value

    return wrapper_decorator

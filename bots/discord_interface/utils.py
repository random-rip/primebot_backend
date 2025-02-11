import functools
import os
from typing import Callable, Union

import discord
from asgiref.sync import sync_to_async
from discord import Colour, Embed, Forbidden, Interaction, Webhook
from discord.ext import commands
from discord.ext.commands import Context
from django.conf import settings
from django.utils import translation

from app_prime_league.models import Channel, Team
from app_prime_league.models.channel import ChannelTeam
from app_prime_league.models.team_and_match import SettingIsFalseException
from bots.messages.base import BaseMessage, MessageNotImplementedError
from utils.messages_logger import log_from_discord

MENTION_PREFIX = "<@&"
MENTION_POSTFIX = ">"

COLOR_NOTIFICATION = Colour.gold()
COLOR_SETTINGS = Colour.greyple()  # deprecated


class ChannelInUse(commands.CheckFailure):
    pass


class TeamInUse(commands.CommandError):
    pass


class AlreadyRegistered(commands.CommandError):
    """
    The team is already registered in the channel
    """

    pass


class NoWebhookPermissions(commands.CommandError):
    pass


class ChannelNotRegistered(commands.CheckFailure):
    pass


class NoTeamRegistered(commands.CheckFailure):
    pass


class WrongChannelType(commands.CheckFailure):
    pass


class DiscordHelper:
    @staticmethod
    def create_msg_arguments(*, msg: BaseMessage, discord_role_id: str | None, color=COLOR_NOTIFICATION, **kwargs):
        arguments = kwargs
        title = msg.generate_title()
        try:
            arguments["embed"] = msg.generate_discord_embed()
        except MessageNotImplementedError:
            arguments["embed"] = Embed(
                title=title,
                description=msg.generate_message(),
                color=color,
            )
        try:
            arguments["poll"] = msg.generate_poll()
        except (MessageNotImplementedError, SettingIsFalseException):
            pass
        arguments["content"] = DiscordHelper.mask_message_with_mention(discord_role_id=discord_role_id, message=title)
        return arguments

    @staticmethod
    def mask_mention(discord_role_id: str | None) -> str | None:
        if discord_role_id is None:
            return None
        return f"{MENTION_PREFIX}{discord_role_id}{MENTION_POSTFIX}"

    @staticmethod
    def mask_message_with_mention(*, discord_role_id: str | None, message: str = ""):
        return f"{DiscordHelper.mask_mention(discord_role_id)} {message}" if discord_role_id is not None else message

    @staticmethod
    async def recreate_webhook(ctx) -> Webhook:
        """
        Raises:
            NoWebhookPermissions
        """
        channel = ctx.message.channel
        try:
            all_webhooks = await channel.webhooks()
            old_webhooks = [webhook for webhook in all_webhooks if settings.DISCORD_APP_CLIENT_ID == webhook.user.id]
            with open(os.path.join(settings.BASE_DIR, "documents", "primebot_logo.jpg"), "rb") as image_file:
                avatar = image_file.read()
            new_webhook = await channel.create_webhook(name="PrimeBot", avatar=avatar)
            for webhook in old_webhooks:
                await webhook.delete()
        except (Forbidden, Exception) as e:
            await log_from_discord(ctx.interaction, optional=f"{e}")
            raise NoWebhookPermissions
        return new_webhook

    @staticmethod
    async def get_or_create_new_webhook(ctx) -> Webhook:
        """
        Raises:
            NoWebhookPermissions
        """
        channel = ctx.message.channel
        try:
            all_webhooks = await channel.webhooks()
        except (Forbidden, Exception) as e:
            await log_from_discord(ctx.interaction, optional=f"{e}")
            raise NoWebhookPermissions
        webhooks = [webhook for webhook in all_webhooks if settings.DISCORD_APP_CLIENT_ID == webhook.user.id]
        return webhooks[0] if len(webhooks) > 0 else await DiscordHelper.recreate_webhook(ctx)

    @staticmethod
    async def delete_webhooks(channel):
        try:
            all_webhooks = await channel.webhooks()
            old_webhooks = [webhook for webhook in all_webhooks if settings.DISCORD_APP_CLIENT_ID == webhook.user.id]
            for webhook in old_webhooks:
                await webhook.delete()
        except (Forbidden, Exception):
            raise NoWebhookPermissions

    @staticmethod
    async def get_registered_team_by_channel_id(channel_id: int) -> Union[None, Team]:
        return await Team.objects.filter(discord_channel_id=channel_id).afirst()

    @staticmethod
    async def get_registered_teams_by_channel_id(channel_id: int) -> list[Team]:
        return await sync_to_async(Team.objects.filter(channels__discord_channel_id=channel_id).distinct)()

    @staticmethod
    async def team_already_in_channel(team_id: int, channel_id: int) -> bool:
        return await ChannelTeam.objects.filter(
            team_id=team_id,
            channel_id=channel_id,
        ).aexists()


def channel_is_registered() -> Callable:
    """
    Use this as a decorator.
    """

    async def predicate(ctx):
        channel_id = ctx.message.channel.id
        if await Channel.objects.filter(discord_channel_id=channel_id).aexists():
            return True
        raise ChannelNotRegistered

    return commands.check(predicate)


def channel_has_at_least_one_team() -> Callable:
    """
    Use this as a decorator.
    """

    async def predicate(ctx):
        channel_id = ctx.message.channel.id
        if await ChannelTeam.objects.filter(channel__discord_channel_id=channel_id).aexists():
            return True
        raise NoTeamRegistered

    return commands.check(predicate)


def check_channel_type() -> Callable:
    async def predicate(ctx):
        if ctx.channel.type in [
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.voice,
        ]:
            return True
        raise WrongChannelType

    return commands.check(predicate)


async def detect_language(interaction: Interaction) -> str:
    """
    Returns the language code from channel, and if not registered from ``user.locale``.
    Returns: Language code
    """
    channel = await Channel.objects.filter(discord_channel_id=interaction.channel_id).afirst()
    return channel.language if channel else str(interaction.locale)


def translation_override(func):
    """
    Decorator to enable and disable translation. The language is set based on the passed ``Context``. If no context
    is present, the default language from settings will be used.
    """

    @functools.wraps(func)
    async def wrapper_decorator(*args, **kwargs):
        if "interaction" in kwargs:
            interaction = kwargs["interaction"]
        else:
            for arg in args:
                if isinstance(arg, Context):
                    interaction = arg.interaction
                    break
                if isinstance(arg, Interaction):
                    interaction = arg
                    break
            else:
                interaction = None

        language = await detect_language(interaction) if interaction is not None else settings.LANGUAGE_CODE
        translation.activate(language)
        with translation.override(language):
            return await func(*args, **kwargs)

    return wrapper_decorator

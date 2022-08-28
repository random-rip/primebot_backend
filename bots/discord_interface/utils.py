import os
from typing import Callable, Union

from asgiref.sync import sync_to_async
from discord import Colour, Embed, Webhook
from discord.ext import commands
from django.conf import settings

from app_prime_league.models import Team
from bots.messages.base import BaseMessage
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
    def create_msg_arguments(*, msg:BaseMessage, discord_role_id, color=COLOR_NOTIFICATION, **kwargs):
        arguments = kwargs
        arguments["embed"] = Embed(description=msg.generate_message(), color=color)
        arguments["content"] = DiscordHelper.mask_message_with_mention(
            discord_role_id=discord_role_id,
            message=msg.generate_title()
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
        except Exception as e:
            await log_from_discord(ctx.message, optional=f"{e}")
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

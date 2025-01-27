from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Channel
from app_prime_league.models.channel import Platforms
from bots.discord_interface.utils import DiscordHelper, channel_is_registered, translation_override


@commands.hybrid_command(help=_("Recreate the notification webhook"))
@commands.guild_only()
@channel_is_registered()
@translation_override
async def fix(ctx):
    async with ctx.typing():
        webhook = await DiscordHelper.recreate_webhook(ctx)
        channel = await Channel.objects.filter(
            platform=Platforms.DISCORD, discord_channel_id=ctx.message.channel.id
        ).afirst()
        channel.discord_webhook_id = webhook.id
        channel.discord_webhook_token = webhook.token
        await channel.asave()
    await ctx.send(
        _(
            "The webhook has been recreated. "
            "If you still experience problems, check our website {website}/discord/ for help "
            "or join our Discord Server {discord}."
        ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK)
    )


async def setup(bot: commands.Bot) -> None:
    bot.add_command(fix)

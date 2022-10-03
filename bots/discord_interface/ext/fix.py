from asgiref.sync import sync_to_async
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from bots.discord_interface.utils import DiscordHelper, check_channel_in_use


@commands.hybrid_command(help="Recreates the notification webhook", )
@commands.guild_only()
@check_channel_in_use()
async def fix(ctx):
    async with ctx.typing():
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=ctx.message.channel.id)
        webhook = await DiscordHelper.create_new_webhook(ctx)

        team.discord_webhook_id = webhook.id
        team.discord_webhook_token = webhook.token
        await sync_to_async(team.save)()
    await ctx.send(_(
        "The webhook has been recreated. "
        "If you still experience problems, check our website {website}/discord/ for help "
        "or join our Discord Community Server {discord}."
    ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(fix)

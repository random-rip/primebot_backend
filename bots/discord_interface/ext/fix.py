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
        if webhook is None:
            return await ctx.send(_(
                "I lack the permission to manage webhooks. Please make sure I have that permission. "
                "If necessary, wait an hour before running the command again. "
                "If it still doesn't work after that, check our website {website}/discord/ for help."
            ).format(website=settings.SITE_ID))

        team.discord_webhook_id = webhook.id
        team.discord_webhook_token = webhook.token
        await sync_to_async(team.save)()
    await ctx.send(_(
        "The webhook has been recreated. "
        "If you still experience problems, check our website {website}/discord/ for help."
    ).format(website=settings.SITE_ID))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(fix)

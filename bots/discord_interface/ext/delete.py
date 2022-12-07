from asgiref.sync import sync_to_async
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from bots.discord_interface.utils import DiscordHelper, check_channel_in_use, translation_override


@commands.hybrid_command(help="Deletes all channel links to the team")
@commands.guild_only()
@check_channel_in_use()
@translation_override
async def delete(ctx, ):
    async with ctx.typing():
        channel = ctx.message.channel
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel.id)
        await ctx.send(_("Alright, I will delete all links to this channel and the team."))
        await sync_to_async(team.set_discord_null)()
        webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
        for webhook in webhooks:
            await webhook.delete()
    await ctx.send(_(
        "All deleted. Feel free to give us feedback on {discord_link} if you are missing or don't like any "
        "functionality. Bye! ✌\n"
        "_The team can now be registered in another channel, or another team can be registered in this channel._"
    ).format(discord_link=settings.DISCORD_SERVER_LINK))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(delete)

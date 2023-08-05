import typing

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from bots.discord_interface.utils import COLOR_SETTINGS, DiscordHelper, check_channel_in_use, translation_override
from core.settings_maker import SettingsMaker


@commands.hybrid_command(name="role", help="Sets a Discord role that will be used in notifications.")
@commands.guild_only()
@check_channel_in_use()
@translation_override
async def set_role(
    ctx,
    role: typing.Optional[discord.Role],
):
    async with ctx.typing():
        channel_id = ctx.message.channel.id
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel_id)
        if role is None:
            team.discord_role_id = None
            await sync_to_async(team.save)()
            await ctx.send(
                _(
                    "All right, I've removed the role mention. "
                    "You can turn it back on if needed, just use `/role ROLE_NAME`."
                )
            )
            return
        if role.name == "@everyone":
            await ctx.send(_("You can't use role **everyone**. Please choose a different role."))
            return

        team.discord_role_id = role.id
        await sync_to_async(team.save)()
    await ctx.send(
        _("Okay, I'll inform the role **{role_name}** for new notifications from now on. 📯").format(role_name=role.name)
    )


@commands.hybrid_command(
    name="settings",
    help="Creates a temporary link to make notification settings",
)
@commands.guild_only()
@check_channel_in_use()
@translation_override
async def team_settings(
    ctx,
):
    async with ctx.typing(ephemeral=True):
        channel_id = ctx.message.channel.id
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel_id)
        maker = await sync_to_async(SettingsMaker)(team=team)
        link = await sync_to_async(maker.generate_expiring_link)(platform="discord")
        embed = discord.Embed(
            title=_("Change settings for {team}").format(team=team.name),
            url=link,
            description=_(
                "The link is only valid for {minutes} minutes. After that, a new link must be generated."
            ).format(minutes=settings.TEMP_LINK_TIMEOUT_MINUTES),
            color=COLOR_SETTINGS,
        )
    await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    bot.add_command(set_role)
    bot.add_command(team_settings)

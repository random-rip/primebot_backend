from discord import Embed
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from bots.discord_interface.utils import COLOR_NOTIFICATION, translation_override


@commands.hybrid_command(
    name="help",
    help=_("Create an overview of the bot and commands"),
)
@translation_override
async def bot_help(
    ctx: commands.Context,
) -> None:
    async with ctx.typing():
        embed = Embed(title=_("Help"), color=COLOR_NOTIFICATION)
        for command in ctx.bot.commands:
            name = f"📌 /{command.qualified_name}"
            value = command.help
            embed.add_field(name=name, value=value, inline=False)

        general = _(
            "ℹ️ **Join our [Discord Server]({discord_url}) for help** ℹ️\n\n"
            "🌐 Checkout our [Website]({website}) for the Calendar integration 📅 and API 🔥\n\n"
            "️️🖥️ Checkout our [Github]({github_url}) for contributions ️️and issues 🐞"
        ).format(
            discord_url=settings.DISCORD_SERVER_LINK,
            website=settings.SITE_ID,
            github_url=settings.GITHUB_URL,
        )
        embed.description = f"{general}\n\n"

        disclaimer = _(
            "_This bot was not created in cooperation with Prime League or Freaks4u Gaming GmbH. "
            "This bot was designed and programmed due to missed matches. "
            "The bot was realized to the best of our knowledge, "
            "and after a test phase made available for other teams.\n"
            "Nevertheless all information is without guarantee!_"
        )
        embed.add_field(name=_("Disclaimer"), value=disclaimer, inline=False)

    await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bot_help)

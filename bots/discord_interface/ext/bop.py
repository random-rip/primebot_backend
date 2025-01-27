from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from django.utils.translation import gettext as _

from bots.base.bop import GIFinator
from bots.discord_interface.utils import translation_override


@commands.hybrid_command(help="What's boppin'?")
@translation_override
async def bop(ctx: commands.Context):
    async with ctx.typing():
        try:
            url = GIFinator.get_gif()
        except ConnectionError:
            await ctx.send(_("It's not my fault, but I can't get you your surprise. :("))
            return
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            buffer = BytesIO(await resp.read())
    await ctx.send(file=discord.File(fp=buffer, filename="bop.gif"))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bop)

from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from django.utils.translation import gettext as _

from bots.base.bop import GIFinator


@commands.hybrid_command(help="What's boppin'?", )
async def bop(ctx: commands.Context, ) -> None:
    async with ctx.typing():
        url = GIFinator.get_gif()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                buffer = BytesIO(await resp.read())
    await ctx.send(file=discord.File(fp=buffer, filename="bop.gif"))


@bop.error
async def bop_error(ctx, error):
    if isinstance(error, ConnectionError):
        await ctx.send(_("It's not my fault, but I can't get you your surprise. :("))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bop)

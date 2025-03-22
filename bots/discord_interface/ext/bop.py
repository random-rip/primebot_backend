from io import BytesIO
from typing import List, Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from django.utils.translation import gettext as _

from bots.base.bop import Gifinator
from bots.discord_interface.utils import translation_override


async def animal_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=animal, value=animal)
        for animal in Gifinator.animals()
        if current.lower() in animal.lower()
    ]


@commands.hybrid_command(help=_("What's boppin'?"))
@app_commands.autocomplete(animal=animal_autocomplete)
@translation_override
async def bop(ctx: commands.Context, animal: Optional[str] = None):
    async with ctx.typing():
        try:
            url = Gifinator.get_gif(animal=animal)
        except ValueError:
            await ctx.send(_("I don't know that animal. :("))
            return
        except ConnectionError:
            await ctx.send(_("Something went wrong this time, but just try again. :)"))
            return
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            buffer = BytesIO(await resp.read())
    await ctx.send(file=discord.File(fp=buffer, filename="bop.gif"))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bop)

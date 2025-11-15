from io import BytesIO
from typing import List, Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from django.utils.translation import gettext as _
from PIL import Image

from bots.base.bop import Gifinator, InvalidAnimalException
from bots.discord_interface.utils import translation_override


async def animal_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=label, value=value)
        for label, value in Gifinator.get_choices()
        if current.lower() in label
    ]


async def process_content(buffer: BytesIO) -> tuple[BytesIO, str]:
    img = Image.open(buffer)
    new_buffer = BytesIO()
    if img.format == "GIF":
        img.save(new_buffer, save_all=True, format=img.format, optimize=True, loop=0)
    else:
        img.thumbnail((512, 512))
        img.save(
            new_buffer,
            format=img.format,
            optimize=True,
        )
    img.close()
    new_buffer.seek(0)
    return new_buffer, img.format.lower()


async def get_content(animal) -> BytesIO:
    """
    Retrieve an image from a URL, ensuring it does not exceed MAX_SIZE.
    If the image exceeds MAX_SIZE, get a new URL and try again.
    """
    max_size = 7 * 1024 * 1024  # 7 MB limit. Discord has 8 MB limit for files.
    max_iterations = 3
    current_iteration = 0
    while current_iteration < max_iterations:
        current_iteration += 1
        try:
            url = Gifinator.get_gif(animal=animal)
        except InvalidAnimalException:
            raise
        except ConnectionError:
            if current_iteration >= max_iterations:
                raise
            continue
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            buffer = BytesIO(await resp.read())
        if len(buffer.getvalue()) <= max_size:
            return buffer
    raise ConnectionError()


@commands.hybrid_command(help=_("What's boppin'?"))
@app_commands.autocomplete(animal=animal_autocomplete)
@translation_override
async def bop(ctx: commands.Context, animal: Optional[str] = None):
    async with ctx.typing():
        try:
            buffer = await get_content(animal)
        except InvalidAnimalException:
            await ctx.send(_("I don't know that animal. :("))
            return
        except ConnectionError:
            await ctx.send(_("Something went wrong this time, but just try again. :)"))
            return
    new_buffer, extension = await process_content(buffer)
    await ctx.send(file=discord.File(fp=new_buffer, filename=f"bop.{extension}"))


async def setup(bot: commands.Bot) -> None:
    bot.add_command(bop)

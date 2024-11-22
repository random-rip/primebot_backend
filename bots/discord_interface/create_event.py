import io
import logging
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from asgiref.sync import async_to_sync, sync_to_async
from discord import EntityType, HTTPException, PrivacyLevel
from django.conf import settings
from niquests import AsyncSession
from PIL import Image, ImageDraw

from app_prime_league.models import Match, Team
from bots.discord_interface.discord_bot import DiscordBot
from bots.messages.helpers import MatchDisplayHelper
from core.cluster_job import Job

logger = logging.getLogger("discord")


async def get_default():
    with open(settings.IMAGE_STATIC_DIR / "square_default.jpg", "rb") as f:
        return f.read()


async def fetch_logo(url: Optional[str]) -> bytes:
    async with AsyncSession() as s:
        try:
            response = await s.get(url)
        except Exception as e:
            logger.exception(f"Could not fetch logo from {url}, using default", e)
            return await get_default()
        else:
            if response.ok:
                return response.content
            logger.error(f"{url} returned status code {response.status_code}, using default")
            return await get_default()


def draw_line(draw, cover_width, cover_height, color):
    line_width = 20
    x_center = cover_width // 2
    draw.line([(x_center, 0), (x_center, cover_height)], fill=color, width=line_width)


async def create_cover_image(team1_url, team2_url):
    team1_image_bytes = await fetch_logo(team1_url)
    team2_image_bytes = await fetch_logo(team2_url)
    team1_image = Image.open(io.BytesIO(team1_image_bytes))
    team2_image = Image.open(io.BytesIO(team2_image_bytes))

    team1_image = team1_image.resize((400, 400), Image.Resampling.BICUBIC)
    team2_image = team2_image.resize((400, 400), Image.Resampling.BICUBIC)

    cover_width = 800
    cover_height = 320
    cover_image = Image.new('RGB', (cover_width, cover_height), (255, 255, 255))

    team1_position = (cover_width // 2 - team1_image.width, cover_height // 2 - team1_image.height // 2)
    team2_position = (cover_width // 2, cover_height // 2 - team2_image.height // 2)

    cover_image.paste(team1_image, team1_position)
    cover_image.paste(team2_image, team2_position)

    draw = ImageDraw.Draw(cover_image)
    lightning_color = '#F1C40F'
    draw_line(draw, cover_width, cover_height, lightning_color)

    img_byte_arr = io.BytesIO()
    cover_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()


async def create_discord_event(match: Match):
    client = await DiscordBot().client

    team = await sync_to_async(Team.objects.get)(id=match.team_id)
    enemy_team = await sync_to_async(Team.objects.get)(id=match.enemy_team_id)
    title = f"{team.name} vs. {enemy_team.name}"
    image = await create_cover_image(team.logo_url, enemy_team.logo_url)

    guild = await client.fetch_guild(team.discord_guild_id)
    try:
        event = await guild.create_scheduled_event(
            name=title,
            start_time=match.begin - timedelta(minutes=15),
            end_time=match.begin + timedelta(hours=2),
            privacy_level=PrivacyLevel.guild_only,
            entity_type=EntityType.external,
            location=match.prime_league_link,
            image=image,
            description=MatchDisplayHelper.display_match_day(match),
        )
    except HTTPException as e:
        logger.exception(f"Could not create event for match {match.id}", e)
        raise e
    else:
        return f"Event {event} created successfully"


class CreateDiscordEventJob(Job):
    def __init__(self, match: Match):
        self.match = match

    def get_kwargs(self) -> Dict:
        return {"match": self.match}

    def function_to_execute(self) -> Callable:
        return async_to_sync(create_discord_event)

    def q_options(self) -> Dict[str, Any]:
        return {
            "cluster": "messages",
            "group": f"POLL {self.match}",
        }

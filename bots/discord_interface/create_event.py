import logging
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from asgiref.sync import async_to_sync, sync_to_async
from discord import EntityType, HTTPException, PrivacyLevel
from django.conf import settings
from niquests import AsyncSession

from app_prime_league.models import Match, Team
from bots.discord_interface.discord_bot import DiscordBot
from bots.messages.helpers import MatchDisplayHelper
from core.cluster_job import Job

logger = logging.getLogger("discord")


async def fetch_logo(url) -> Optional[bytes]:
    async with AsyncSession() as s:
        response = await s.get(url)
        return response.content


async def create_discord_event(match: Match):
    client = await DiscordBot().client
    guild = await client.fetch_guild(settings.DISCORD_GUILD_ID)

    team = await sync_to_async(Team.objects.get)(id=match.team_id)
    enemy_team = await sync_to_async(Team.objects.get)(id=match.enemy_team_id)
    title = f"{team.name} vs. {enemy_team.name}"
    image = await fetch_logo(team.logo_url)
    try:
        event = await guild.create_scheduled_event(
            name=title,
            start_time=match.begin,
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

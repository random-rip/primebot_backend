import asyncio
import logging
from itertools import cycle

from asgiref.sync import sync_to_async
from discord.ext import commands
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import ScoutingWebsite
from app_prime_league.models.channel import Channel, ChannelTeam, Platforms
from app_prime_league.teams import register_team
from bots.discord_interface.utils import (
    DiscordHelper,
    NoWebhookPermissions,
    WrongChannelType,
    check_channel_type,
    translation_override,
)
from bots.messages import MatchesOverview
from utils.exceptions import (
    CouldNotParseURLException,
    Div1orDiv2TeamException,
    PrimeLeagueConnectionException,
    TeamWebsite404Exception,
)
from utils.utils import get_valid_team_id


class TeamIDConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            team_id = get_valid_team_id(argument)
        except CouldNotParseURLException:
            raise commands.BadArgument()

        return team_id


async def load_in_background(ctx: commands.Context, team_id: int):
    await ctx.send(_("I'm setting up the team registration for you (estimated time: 40 seconds)."))
    clock_steps = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    msg = _("Please wait a moment...")
    loading_message = await ctx.send(f"{msg} {clock_steps[0]}")

    # Start the registration process in a background task
    registration_task = asyncio.create_task(sync_to_async(register_team)(team_id=team_id))

    for c in cycle(clock_steps):
        if registration_task.done():
            await loading_message.delete()
            break
        await loading_message.edit(content=f"{msg} {c}")
        await asyncio.sleep(0.5)
    return await registration_task


@commands.hybrid_command(help=_("Register the given Prime League team in the channel"))
@commands.guild_only()
@check_channel_type()
@translation_override
async def start(ctx: commands.Context, team_id_or_url: TeamIDConverter):
    async with ctx.typing():
        team_id: int = team_id_or_url
        channel_id = ctx.channel.id

        if await ChannelTeam.objects.filter(
            team_id=team_id,
            channel__discord_channel_id=channel_id,
        ).aexists():
            return await ctx.send(_("This team is already registered in this channel."))

        webhook = await DiscordHelper.get_or_create_new_webhook(ctx)

        try:
            team = await load_in_background(ctx, team_id)
        except TeamWebsite404Exception:
            return await ctx.send(
                _("The team was not found on the Prime League website. Make sure you register the proper team."),
            )
        except PrimeLeagueConnectionException:
            return await ctx.send(
                _(
                    "Currently unable to connect to the Prime League website. Try again in a few hours.\n"
                    "If it still doesn't work later, join our [Discord Server]({discord}) for help."
                ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK)
            )

        channel, created = await Channel.objects.aget_or_create(
            discord_channel_id=ctx.channel.id,
            platform=Platforms.DISCORD,
            defaults={
                "discord_guild_id": ctx.guild.id,
                "discord_channel_id": channel_id,
                "discord_webhook_id": webhook.id,
                "discord_webhook_token": webhook.token,
            },
        )
        channel_team = await ChannelTeam.objects.acreate(channel=channel, team=team)

        response = _(
            "Perfect, this channel was registered for team **{team_name}**.\n"
            "The most important commands:\n"
            "📌 `/role` - to set a role to be mentioned in notifications\n"
            "📌 `/settings` - to personalize the notifications, change the PrimeBot language or change the "
            "scouting website (default: {scouting_website})\n"
            "📌 `/matches` - to get an overview of the matches that are still open\n"
            "📌 `/match` - to receive detailed information about a match day\n\n"
            "Just try it out! 🎁 \n"
            "The **status of the Prime League API** can be viewed at any time on {website}."
        ).format(team_name=team.name, website=settings.SITE_ID, scouting_website=ScoutingWebsite.default().name)
        msg = await sync_to_async(MatchesOverview)(channel_team=channel_team, match_ids=None)
        embed = await sync_to_async(msg.generate_discord_embed)()
        return await ctx.send(response, embed=embed)


@start.error
@translation_override
async def start_error(ctx, error):
    error = getattr(error, 'original', error)
    if isinstance(error, commands.BadArgument):
        return await ctx.reply(
            _(
                "No Team ID could be found from the passed argument.\n"
                "Join our [Discord Server]({discord}) for help or checkout our [Website]({website})."
            ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK)
        )
    elif isinstance(error, Div1orDiv2TeamException):
        return await ctx.send(_("No teams from Division 1 or 2 can be registered."))
    elif isinstance(error, WrongChannelType):
        return await ctx.send(
            _("Only Text, Voice and News channels are supported. Please use one of these channel types.")
        )
    elif isinstance(error, NoWebhookPermissions):
        return await ctx.reply(
            _(
                "I lack the permission to manage webhooks. Please make sure I have that permission. "
                "Join our [Discord Server]({discord}) for help or checkout our [Website]({website})."
            ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK)
        )
    logging.getLogger("commands").exception(error)
    return await ctx.reply(
        _("An unknown error has occurred. Please contact the developers on [Discord]({discord}).").format(
            discord=settings.DISCORD_SERVER_LINK
        ),
        suppress_embeds=True,
    )


async def setup(bot: commands.Bot) -> None:
    bot.add_command(start)

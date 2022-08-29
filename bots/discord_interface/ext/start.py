import logging

from asgiref.sync import sync_to_async
from discord.ext import commands
from discord.ext.commands import BadArgument
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.teams import register_team
from bots.discord_interface.utils import (
    DiscordHelper, ChannelInUse, TeamInUse, NoWebhookPermissions, check_channel_not_in_use, check_team_not_registered)
from bots.messages import MatchesOverview
from utils.exceptions import (
    CouldNotParseURLException, TeamWebsite404Exception, PrimeLeagueConnectionException, Div1orDiv2TeamException)
from utils.utils import get_valid_team_id


class TeamIDConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            team_id = get_valid_team_id(argument)
        except CouldNotParseURLException:
            raise BadArgument()

        return team_id


@commands.hybrid_command(help="Registers the Prime League team in the channel")
@commands.guild_only()
@check_channel_not_in_use()
async def start(ctx: commands.Context, team_id_or_url: TeamIDConverter):
    team_id = team_id_or_url
    await check_team_not_registered(team_id)

    webhook = await DiscordHelper.create_new_webhook(ctx)
    if webhook is None:
        raise NoWebhookPermissions

    async with ctx.typing():
        await ctx.send(_(
            "All right, I'll see what I can find on this.\n"
            "This may take a moment...⏳\n"
        ))
        try:
            team = await sync_to_async(register_team)(
                team_id=team_id, discord_webhook_id=webhook.id,
                discord_webhook_token=webhook.token, discord_channel_id=ctx.channel.id
            )
        except TeamWebsite404Exception:
            return await ctx.send(_(
                "The team was not found on the Prime League website. Make sure you register the proper team."
            ))

        except PrimeLeagueConnectionException:
            return await ctx.send(_(
                "Currently unable to connect to the Prime League website. Try again in a few hours.\n"
                "If it still doesn't work later, check our website {website} for help "
                "or join our Discord Community Server {discord}."
            ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK))

    msg = await sync_to_async(MatchesOverview)(team=team)
    embed = await sync_to_async(msg.generate_discord_embed)()
    response = _(
        "Perfect, this channel was registered for team **{team_name}**.\n"
        "The most important commands:\n"
        "📌 `/role ROLE_NAME` - to set a role to be mentioned in notifications\n\n"
        "📌 `/settings` - to personalize the notifications, set the language to English or change the "
        "scouting website (default: op.gg)\n"
        "📌 `/matches` - to get an overview of the matches that are still open\n"
        "📌 `/match MATCH_DAY` - to receive detailed information about a match day\n\n"
        "Just try it out! 🎁 \n"
        "The **status of the Prime League API** can be viewed at any time on {website}."
    ).format(team_name=team.name, website=settings.SITE_ID)
    return await ctx.send(response, embed=embed)


@start.error
async def start_error(ctx, error):
    error = getattr(error, 'original', error)
    if isinstance(error, commands.BadArgument):
        return await ctx.reply(_(
            "No ID could be found from the passed argument.\nCheck out our website {website} for help "
            "or join our Discord Community Server {discord}."
        ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK))
    elif isinstance(error, Div1orDiv2TeamException):
        return await ctx.send(_("No teams from Division 1 or 2 can be registered."))
    elif isinstance(error, ChannelInUse):
        return await ctx.reply(_(
            "There is already a team registered for this channel. If you want to register another team here, "
            "first delete the link to the current team with `/delete`. If no more notifications arrive in the channel, "
            "but you have already registered the team, please use `/fix`."
        ))
    elif isinstance(error, TeamInUse):
        return await ctx.reply(_(
            "This team is already registered in another channel. "
            "First delete the link in the other channel with `/delete`.\n Check our website {website} for help "
            "or join our Discord Community Server {discord}."
        ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK))
    elif isinstance(error, NoWebhookPermissions):
        return await ctx.reply(_(
                "I lack the permission to manage webhooks. Please make sure I have that permission. "
                "If necessary, wait an hour before running the command again. "
                "If it still doesn't work after that, check our website {website}/ for help "
                "or join our Discord Community Server {discord}."
            ).format(website=settings.SITE_ID, discord=settings.DISCORD_SERVER_LINK))
    logging.getLogger("commands").exception(error)
    return await ctx.reply(_(
        "An unknown error has occurred. Please contact the developers on Discord at {discord_link}."
    ).format(discord_link=settings.DISCORD_SERVER_LINK), suppress_embeds=True)


async def setup(bot: commands.Bot) -> None:
    bot.add_command(start)

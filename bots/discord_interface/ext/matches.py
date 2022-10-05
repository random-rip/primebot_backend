from asgiref.sync import sync_to_async
from discord.ext import commands

from bots.discord_interface.discord_bot import discord_logger
from bots.discord_interface.utils import DiscordHelper, check_channel_in_use
from bots.messages import MatchesOverview, MatchOverview


@commands.hybrid_command(help="Creates an overview for open matches", )
@commands.guild_only()
@check_channel_in_use()
async def matches(ctx, ):
    async with ctx.typing():
        channel_id = ctx.message.channel.id
        team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=channel_id)
        msg = await sync_to_async(MatchesOverview)(team=team)
        embed = await sync_to_async(msg.generate_discord_embed)()
    await ctx.send(embed=embed)


@commands.hybrid_command(name="match", help="Creates an overview for a given match day", )
@commands.guild_only()
@check_channel_in_use()
async def match_information(ctx, match_day: int, ):
    async with ctx.typing():
        try:
            team = await DiscordHelper.get_registered_team_by_channel_id(channel_id=ctx.message.channel.id)
            found_matches = await sync_to_async(list)(
                await sync_to_async(team.get_obvious_matches_based_on_stage)(match_day=match_day))
            if not found_matches:
                return await ctx.send("This match day was not found. Try `/match 1`.")
            for i in found_matches:

                msg = await sync_to_async(MatchOverview)(team=team, match=i)
                embed = await sync_to_async(msg.generate_discord_embed)()
                await ctx.send(embed=embed)
        except Exception as e:
            discord_logger.exception(e, exc_info=True)
            raise


async def setup(bot: commands.Bot) -> None:
    bot.add_command(matches)
    bot.add_command(match_information)

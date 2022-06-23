import logging
import os
import re
from io import BytesIO

import aiohttp
from asgiref.sync import sync_to_async
from discord import Webhook, RequestsWebhookAdapter, Embed, Colour, NotFound, File
from discord.ext import commands
from django.conf import settings

from app_api.modules.team_settings.maker import SettingsMaker
from app_prime_league.models import Team, Match
from app_prime_league.teams import register_team
from bots.base.bop import GIFinator
from bots.base.bot import Bot
from bots.messages import MatchesOverview, MatchOverview
from bots.messages.base import BaseMessage
from bots.utils import mysql_has_gone_away
from utils.changelogs import CHANGELOGS
from utils.exceptions import CouldNotParseURLException, PrimeLeagueConnectionException, TeamWebsite404Exception, \
    Div1orDiv2TeamException
from utils.messages_logger import log_from_discord
from utils.utils import get_valid_team_id

MENTION_PREFIX = "<@&"
MENTION_POSTFIX = ">"

COLOR_NOTIFICATION = Colour.gold()
COLOR_SETTINGS = Colour.greyple()

notifications_logger = logging.getLogger("notifications")


class DiscordBot(Bot):
    """
    DiscordBot Class. Provides Communication with Bot(Discord API) and Client
    """

    def __init__(self):
        help_command = commands.DefaultHelpCommand(
            no_category='Commands'
        )

        super().__init__(
            bot=commands.Bot,
            bot_config={
                "token": settings.DISCORD_BOT_KEY,
                "command_prefix": '!',
                "description": (
                    "Dieser Bot ist nicht in Kooperation mit der Prime League bzw. der Freaks4u Gaming GmbH entstanden "
                    "und hat damit keinen direkten Bezug zur Prime League. Dieser Bot wurde aufgrund von versäumten "
                    "Matches entworfen und programmiert. Der Bot wurde nach bestem Gewissen realisiert, und nach einer "
                    "Testphase für andere Teams zur Verfügung gestellt.\n"
                    "Dennoch sind alle Angaben ohne Gewähr! _Version: {version}_"
                ).format(
                    version=CHANGELOGS[sorted(CHANGELOGS.keys())[-1]]["version"]),
                "help_command": help_command
            },
        )

    def _initialize(self):
        @self.bot.command(name='start', help="Registriert das Team im Channel (Beispiel: !start 105959)",
                          pass_context=True, )
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def start(ctx, team_id_or_url=None):
            try:
                team_id = get_valid_team_id(team_id_or_url)
            except CouldNotParseURLException:
                await ctx.send(
                    content=(
                        "Aus dem Übergabeparameter konnte keine ID gefunden werden. "
                        "(Format `!start TEAM_ID_or_TEAM_URL`).\n"
                        "Schaue auf unserer Website https://primebot.me/discord/ nach Hilfe."
                    ))
                return
            except Div1orDiv2TeamException:
                await ctx.send(
                    content=(
                        "Es können keine Teams aus Division 1 oder 2 registriert werden."
                    ))
                return

            channel_id = ctx.message.channel.id
            if await get_registered_team_by_channel_id(channel_id=channel_id) is not None:
                await ctx.send(
                    content=(
                        "Für diesen Channel ist bereits ein Team registriert. Falls du hier ein anderes Team "
                        "registrieren möchtest, lösche zuerst die Verknüpfung zum aktuellen Team mit `!delete`. "
                        "Wenn keine Benachrichtigungen mehr in dem Channel ankommen, "
                        "aber du das Team bereits registriert hast, benutze bitte `!fix`."
                    )
                )
                return
            if await get_registered_team_by_team_id(team_id) is not None:
                await ctx.send(
                    content=(
                        "Dieses Team ist bereits in einem anderen Channel registriert. "
                        "Lösche zuerst die Verknüpfung im anderen Channel mit `!delete`.\n"
                        "Schaue auf unserer Website https://primebot.me/discord/ nach Hilfe."
                    )
                )
                return

            webhook = await _create_new_webhook(ctx)
            if webhook is None:
                await ctx.send(
                    content=(
                        "Mir fehlt die Berechtigung, Webhooks zu verwalten. "
                        "Bitte stelle sicher, dass ich diese Berechtigung habe. "
                        "Gegebenenfalls warte eine Stunde, bevor du den Befehl wieder ausführst. "
                        f"Falls es danach noch nicht gehen sollte, schaue auf unserer Website "
                        f"https://primebot.me/discord/ nach Hilfe."
                    ),
                )
                return
            await ctx.send(
                content=(
                    "Alles klar, ich schaue, was ich dazu finden kann.\n"
                    "Das kann einen Moment dauern...⏳\n"
                )
            )
            async with ctx.typing():
                try:
                    team = await sync_to_async(
                        register_team)(team_id=team_id, discord_webhook_id=webhook.id,
                                       discord_webhook_token=webhook.token, discord_channel_id=channel_id)
                except TeamWebsite404Exception:
                    await ctx.send(
                        content=(
                            "Das Team wurde nicht auf der PrimeLeague Website gefunden. "
                            "Stelle sicher, dass du das richtige Team registrierst."
                        )
                    )
                    return
                except PrimeLeagueConnectionException:
                    await ctx.send(
                        content=(
                            "Momentan kann keine Verbindung zu der PrimeLeague Website hergestellt werden. "
                            "Probiere es in ein paar Stunden noch einmal.\n"
                            f"Wenn es später immer noch nicht funktioniert, "
                            f"schaue auf unserer Website https://primebot.me/crew/ nach Hilfe."
                        )
                    )
                    return

            msg = await sync_to_async(MatchesOverview)(team=team)
            embed = await sync_to_async(msg.generate_discord_embed)()
            await ctx.send(embed=embed)
            await ctx.send(
                content=(
                    "Perfekt, dieser Channel wurde für Team **{team_name}** registriert.\n"
                    "Die wichtigsten Befehle:\n"
                    "📌 `!role ROLE_NAME` - um eine Rolle zu setzen, die bei Benachrichtigungen erwähnt werden soll\n"
                    "📌 `!settings` - um die Benachrichtigungen zu personalisieren, die Sprache auf englisch zu stellen "
                    "oder die Scouting Website (Standard: op.gg) zu ändern\n"
                    "📌 `!matches` - um eine Übersicht der noch offenen Matches zu erhalten\n"
                    "📌 `!match MATCH_DAY` - um detaillierte Informationen zu einem Spieltag zu erhalten\n\n"
                    "Einfach ausprobieren! 🎁 \n"
                    "Der **Status der Prime League API** kann jederzeit auf https://primebot.me/ angeschaut werden. "
                ).format(team_name=team.name)
            )

        @self.bot.command(name="fix", help="Erstellt den Benachrichtigungswebhook neu", pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def fix(ctx):
            channel = ctx.message.channel
            team = await get_registered_team_by_channel_id(channel_id=channel.id)
            if team is None:
                return await channel_not_registered(ctx)
            async with ctx.typing():
                webhook = await _create_new_webhook(ctx)
                if webhook is None:
                    await ctx.send(
                        content=(
                            "Mir fehlt die Berechtigung, Webhooks zu verwalten. "
                            "Bitte stelle sicher, dass ich diese Berechtigung habe. "
                            "Gegebenenfalls warte eine Stunde, bevor du den Befehl wieder ausführst. "
                            f"Falls es danach noch nicht gehen sollte, schaue auf unserer Website "
                            f"https://primebot.me/discord/ nach Hilfe."
                        ),
                    )
                    return
                team.discord_webhook_id = webhook.id
                team.discord_webhook_token = webhook.token
                await sync_to_async(team.save)()
            await ctx.send(
                content=(
                    "Webhook wurde neu erstellt. Sollten weiterhin Probleme auftreten, schaue auf unserer "
                    "Website https://primebot.me/discord/ nach Hilfe."
                )
            )

        @self.bot.command(name="role", help=(
                "Setze eine Discordrolle, die in den Benachrichtigungen benutzt wird. "
                "Um die Rolle zu entfernen schreibe !role ohne Parameter"
        )
            , pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def set_role(ctx, *role_name, ):

            channel_id = ctx.message.channel.id
            team = await get_registered_team_by_channel_id(channel_id=channel_id)
            if team is None:
                return await channel_not_registered(ctx)
            role_name = " ".join(role_name) if len(role_name) > 0 else None
            if role_name is None:
                team.discord_role_id = None
                await sync_to_async(team.save)()
                await ctx.send(
                    content=(
                        "Alles klar, ich habe die Rollenerwähnung entfernt. "
                        "Du kannst sie bei Bedarf wieder einschalten, benutze dazu einfach `!role ROLE_NAME`."
                    ),
                )
                return

            role = await parse_role(role_name, roles=ctx.message.author.guild.roles)
            if role is None:
                await ctx.send(
                    content=(
                        "Die Rolle {role_name} habe ich nicht gefunden. Stelle sicher, dass diese Rolle existiert."
                    ).format(role_name=role_name)
                )
                return
            team.discord_role_id = role.id
            await sync_to_async(team.save)()
            await ctx.send(
                content=(
                    "Okay, ich informiere die Rolle **@{role_name}** ab jetzt bei neuen Benachrichtigungen. 📯"
                ).format(role_name=role.name)
            )
            return

        @self.bot.command(name="bop", help="What's boppin'?", pass_context=True)
        @commands.check(log_from_discord)
        async def bop(ctx):
            try:
                url = GIFinator.get_gif()
            except ConnectionError:
                await ctx.send("It's not my fault, but I can't get you your surprise. :(")
                return
            async with ctx.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        buffer = BytesIO(await resp.read())
            await ctx.send(file=File(fp=buffer, filename="bop.gif"))

        @self.bot.command(name="matches", help="Erstellt eine Übersicht für die offenen Spiele", pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def matches(ctx, ):
            channel_id = ctx.message.channel.id
            team = await get_registered_team_by_channel_id(channel_id=channel_id)
            if team is None:
                return await channel_not_registered(ctx)
            msg = await sync_to_async(MatchesOverview)(team=team)
            embed = await sync_to_async(msg.generate_discord_embed)()
            await ctx.send(embed=embed)

        @self.bot.command(name="match", help=(
                "Erstellt eine Übersicht für den übergebenen Spieltag (Beispiel: !match 1)"
        ), pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def match_information(ctx, match_day=None, ):
            channel_id = ctx.message.channel.id
            team = await get_registered_team_by_channel_id(channel_id=channel_id)
            if team is None:
                return await channel_not_registered(ctx)
            try:
                match_day = int(match_day)
            except (TypeError, ValueError):
                await ctx.send(
                    content=(
                        "Dieser Spieltag wurde nicht gefunden gefunden. Probiere es mit `!match 1`."
                    )
                )
                return

            # Multiple matches are possible in tiebreaker matches (they all have `match_day=99` )
            found_matches = await sync_to_async(list)(
                team.matches_against.filter(match_type=Match.MATCH_TYPE_LEAGUE, match_day=match_day).all())
            if not found_matches:
                await ctx.send(
                    content=(
                        "Dieser Spieltag wurde nicht gefunden gefunden. Probiere es mit `!match 1`."
                    )
                )
                return

            for i in found_matches:
                msg = await sync_to_async(MatchOverview)(team=team, match=i)
                embed = await sync_to_async(msg.generate_discord_embed)()
                await ctx.send(embed=embed)
            return

        @self.bot.command(name="delete", help=(
                "Löscht die Channelverknüpfungen zum Team. "
                "Achtung, danach werden keine weiteren Benachrichtigungen gesendet."
        ), pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def delete(ctx, ):

            channel = ctx.message.channel
            team = await get_registered_team_by_channel_id(channel_id=channel.id)
            if team is None:
                return await channel_not_registered(ctx)
            async with ctx.typing():
                await ctx.send(
                    content=(
                        "Alles klar ich lösche alle Verknüpfungen zu diesem Channel und dem Team."
                    ),
                )
            await sync_to_async(team.set_discord_null)()
            async with ctx.typing():
                webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
                await ctx.send(
                    content=(
                        "Alles gelöscht. Gebt uns gerne Feedback auf https://discord.gg/K8bYxJMDzu, falls euch "
                        "Funktionalitäten fehlen oder nicht gefallen. Bye! ✌\n"
                        "_Das Team kann jetzt in einem anderen Channel registriert werden, oder ein anderes Team "
                        "kann in diesem Channel registriert werden._"
                    ),
                )
                for webhook in webhooks:
                    await webhook.delete()
            return

        @self.bot.command(name="settings", help=(
                "Erstellt einen temporären Link um Benachrichtigungseinstellungen vorzunehmen"
        ), pass_context=True)
        @commands.check(mysql_has_gone_away)
        @commands.check(log_from_discord)
        async def team_settings(ctx, ):
            channel_id = ctx.message.channel.id
            team = await get_registered_team_by_channel_id(channel_id=channel_id)
            if team is None:
                return await channel_not_registered(ctx)
            async with ctx.typing():
                maker = await sync_to_async(SettingsMaker)(team=team)
                link = await sync_to_async(maker.generate_expiring_link)(platform="discord")
                embed = Embed(
                    title=(
                        "Einstellungen für {team} ändern"
                    ).format(team=team.name),
                    url=link,
                    description=(
                        "Der Link ist nur {minutes} Minuten gültig. Danach muss ein neuer Link generiert werden."
                    ).format(minutes=settings.TEMP_LINK_TIMEOUT_MINUTES), color=COLOR_SETTINGS)
                await ctx.send(embed=embed)

        async def channel_not_registered(ctx):
            return await ctx.send(
                content=(
                    "In diesem Channel ist derzeitig kein Team registriert. "
                    "Benutze dazu den Befehl `!start TEAM_ID_oder_TEAM_URL`."
                )
            )

        async def _create_new_webhook(ctx):
            channel = ctx.message.channel
            try:
                webhooks = [x for x in await channel.webhooks() if settings.DISCORD_APP_CLIENT_ID == x.user.id]
                with open(os.path.join(settings.BASE_DIR, "documents", "primebot_logo.jpg"), "rb") as image_file:
                    avatar = image_file.read()
                new_webhook = await channel.create_webhook(name="PrimeBot", avatar=avatar)
                for webhook in webhooks:
                    await webhook.delete()
            except Exception as e:
                await log_from_discord(ctx, optional=f"{e}")
                return None
            return new_webhook

        async def get_registered_team_by_channel_id(channel_id):
            """

            :param channel_id: Integer
            :return: Instance of class Team or None
            """
            return await sync_to_async(Team.objects.filter(discord_channel_id=channel_id).first)()

        async def get_registered_team_by_team_id(team_id):
            """

            :param team_id: Integer
            :return: Instance of class Team or None
            """
            return await sync_to_async(Team.objects.filter(id=team_id, discord_webhook_id__isnull=False).first)()

        async def parse_role(value, roles):
            match = re.match(pattern=f"{MENTION_PREFIX}(?P<role_id>[0-9]*){MENTION_POSTFIX}", string=value)
            if match is not None:
                role_id = int(match.group('role_id'))
                for i in roles:
                    if i.id == role_id:
                        return i
            for i in roles:
                if i.name == value:
                    return i
            return None

    def run(self):
        self.bot.run(self.token)

    @staticmethod
    def send_message(*, msg: BaseMessage, team):
        webhook = Webhook.partial(team.discord_webhook_id, team.discord_webhook_token, adapter=RequestsWebhookAdapter())
        try:
            webhook.send(**DiscordBot._create_msg_arguments(discord_role_id=team.discord_role_id, msg=msg))
        except NotFound as e:
            team.set_discord_null()
            notifications_logger.info(f"Could not send message to {team}: {e}. Soft deleted'")
        except Exception as e:
            notifications_logger.exception(f"Could not send message to {team}: '{msg}. -> {e}'")

    @staticmethod
    def mask_mention(discord_role_id):
        if discord_role_id is None:
            return None
        return f"{MENTION_PREFIX}{discord_role_id}{MENTION_POSTFIX}"

    @staticmethod
    def mask_message_with_mention(*, discord_role_id, message: str = ""):
        return f"{DiscordBot.mask_mention(discord_role_id)} {message}" if discord_role_id is not None else message

    @staticmethod
    def _create_msg_arguments(*, msg, discord_role_id, color=COLOR_NOTIFICATION, **kwargs):
        arguments = kwargs
        arguments["embed"] = Embed(description=msg.generate_message(), color=color)
        arguments["content"] = DiscordBot.mask_message_with_mention(
            discord_role_id=discord_role_id,
            message=msg.generate_title()
        )
        return arguments

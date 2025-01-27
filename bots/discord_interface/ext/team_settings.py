import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from django.utils.translation import gettext as _

from app_prime_league.models import Channel, Team
from app_prime_league.models.channel import ChannelTeam
from bots.discord_interface.ui.buttons import BaseTeamButton, CloseButton
from bots.discord_interface.ui.selects import BaseTeamSelect
from bots.discord_interface.ui.views import BaseTeamSelectionView
from bots.discord_interface.utils import channel_is_registered, translation_override
from core.settings_maker import SettingsMaker


class ExternalLinkButton(BaseTeamButton):
    def __init__(self, url, **kwargs):
        super().__init__(style=discord.ButtonStyle.link, url=url, **kwargs)


class TeamSelectionView(BaseTeamSelectionView):

    async def build(self):
        if self.is_select:
            self.add_item(
                BaseTeamSelect(
                    options=self.teams,
                    default=self.selected_team,
                    row=0,
                )
            )
        else:
            channel_teams = ChannelTeam.objects.filter(channel=self.channel).select_related("channel", "team")
            async for channel_team in channel_teams:
                maker = SettingsMaker(channel_team=channel_team)
                url = await sync_to_async(maker.generate_expiring_link)(platform="discord", expiring_at=None)
                self.add_item(
                    ExternalLinkButton(
                        url=url,
                        team=channel_team.team,
                        channel=self.channel,
                        row=0,
                    )
                )
        self.add_item(CloseButton(row=4))

    @translation_override
    async def handle_team_select(self, team: Team, interaction: discord.Interaction, view: "TeamSelectionView"):
        channel_team = await ChannelTeam.objects.aget(channel=self.channel, team=team)
        maker = SettingsMaker(channel_team=channel_team)
        url = await sync_to_async(maker.generate_expiring_link)(platform="discord", expiring_at=None)

        view.clear_items()
        view.selected_team = team
        await view.build()
        view.add_item(
            ExternalLinkButton(
                url=url,
                team=team,
                channel=self.channel,
                label=_("Notification Settings"),
                row=1,
            )
        )
        await interaction.response.edit_message(
            content=None,
            view=view,
        )


@commands.hybrid_command(
    name="settings",
    help=_("Create a temporary link to make notification settings"),
)
@commands.guild_only()
@channel_is_registered()
@translation_override
async def team_settings(
    ctx,
):
    channel = await Channel.objects.aget(discord_channel_id=ctx.message.channel.id)
    teams = await sync_to_async(list)(Team.objects.filter(channels=channel).order_by("name"))
    selected_team = teams[0] if len(teams) == 1 else None
    view = TeamSelectionView(teams=teams, channel=channel, selected_team=selected_team)
    await view.build()
    await ctx.send(
        content=_("Select a team"),
        view=view,
        ephemeral=True,
        delete_after=60 * 10,
    )


async def setup(bot: commands.Bot) -> None:
    bot.add_command(team_settings)

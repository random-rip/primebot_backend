from django.utils.translation import gettext as _

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage


class NewMatchNotification(MatchMessage):
    """
    Teamaktualisierungen generieren keine Benachrichtigungen, deswegen ist die Message silenced.
    (Bisher gedacht für Kalibrierungsspiele, kann aber auf die Starterdivision ausgeweitet werden)
    # TODO implementieren von einem oder mehreren neuen Matches
    """
    settings_key = "NEW_MATCH_NOTIFICATION"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)

    def _generate_title(self):
        return "🔥 " + _('Neues Match')

    def _generate_message(self):
        return _(
            "Euer nächstes Match in der Kalibrierungsphase:\n"
            "🔜[{match_day}]({match_url}) gegen [{enemy_team_tag}]({enemy_team_url}):\n"
            "Hier ist der [{website} Link]({scouting_url}) des Teams."
        ).format(
            match_day=self.helper.display_match_day(self.match),
            match_url=self.match_url,
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            website=self.scouting_website,
            scouting_url=self.enemy_team_scouting_url,
        )

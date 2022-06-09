from app_prime_league.models import Team
from modules.processors.team_processor import TeamDataProcessor


class TeamComparer:

    def __init__(self, team: Team, processor: TeamDataProcessor, ):
        self.team = team
        self.processor = processor

    def compare_new_matches(self):
        """
        Returns: List of integers or False

        """
        new_match_ids = self.processor.get_matches()
        current_match_ids = self.team.matches_against.values_list("match_id", flat=True)
        missing_ids = list(set(new_match_ids) - set(current_match_ids))
        return missing_ids or False

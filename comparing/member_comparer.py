from app_prime_league.models import Player
from data_crawling.api import Crawler
from parsing.parser import TeamHTMLParser


class MemberComparer:

    def __init__(self, team_id, members):
        self.team_id = team_id
        self.members = members

    def compare_members(self):
        crawler = Crawler(local=False)
        website = crawler.get_team_website(self.team_id)
        parser = TeamHTMLParser(website)
        current_members = parser.get_members()
        for member in current_members:
            player = Player.objects.filter(id=member[0], name=member[1], is_leader=member[3])
            if not player.exists():
                player = Player.objects.filter(id=member[0])
                player.update(name=member[1], is_leader=member[3])
        return True

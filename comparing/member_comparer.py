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
        for (id, name, summoner_name, is_leader) in current_members:
            player = Player.objects.filter(id=id, name=name, summoner_name=summoner_name, is_leader=is_leader)
            if not player.exists():
                player, created = Player.objects.get_or_create(id=id, defaults={
                    "name": name,
                })
                if not created:
                    player.update(name=name, summoner_name=summoner_name, is_leader=is_leader)
        return True

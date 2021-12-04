import os

from django.conf import settings
from django.test import TestCase
from modules.data_crawling import get_local_response
from modules.parsing.parser import TeamHTMLParser


class TeamHTMLParserTests(TestCase):

    def setUp(self):
        test_dir = os.path.join(settings.BASE_DIR, "parsing", "tests")
        website = get_local_response(file_name="team_155398.txt", file_path=test_dir)
        self.team_html_parser = TeamHTMLParser(website)

    def test_members(self):
        members = self.team_html_parser.get_members()

        expected = [
            ('1826806', 'Seriouzly', 'Gwens Extase', True),
            ('1851621', 'DieBiene69', 'I bims 1 Biene', False), ('1851689', 'MTYUwU', 'MTY', False),
            ('577395', 'Firefistacer', 'ImLostBro', False), ('1827650', 'TraceVII', 'TraceVII', False),
            ('1592374', 'Meraldis', 'Meraldis', False), ('1827282', 'whltebeard', 'WHlTEBEARD', False),
            ('1826846', 'NiceLikeIce', 'NiceLikeIce', False)
        ]

        self.assertListEqual(members, expected, "Members could not be parsed.")

    def test_logo(self):
        logo = self.team_html_parser.get_logo()
        expected = "https://cdn0.gamesports.net/league_team_logos/155000/155398.jpg?1622736708"
        self.assertEqual(logo, expected, "Logo could not be parsed.")

    def test_team_tag(self):
        tag = self.team_html_parser.get_team_tag()
        expected = "ING"
        self.assertEqual(tag, expected, "Team tag could not be parsed.")

    def test_team_name(self):
        team_name = self.team_html_parser.get_team_name()
        expected = "Insignum Gaming"
        self.assertEqual(team_name, expected, "Team name could not be parsed.")

    def test_current_division(self):
        current_division = self.team_html_parser.get_current_division()
        expected = "Swiss Starter"
        self.assertEqual(current_division, expected, "Current Division could not be parsed.")

    def test_matches(self):
        matches = self.team_html_parser.get_matches()
        expected = ['800094', '801721', '802813', '805889', '806945', '807419']
        self.assertEqual(matches, expected, "Match IDs could not be parsed.")

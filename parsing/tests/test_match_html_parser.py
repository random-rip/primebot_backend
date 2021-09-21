import os

from django.conf import settings
from django.test import TestCase

from app_prime_league.models import Team
from data_crawling.api import get_local_response
from parsing.parser import MatchHTMLParser


class MatchHTMLParserTests(TestCase):

    def setUp(self):
        test_dir = os.path.join(settings.BASE_DIR, "parsing", "tests")
        website = get_local_response(file_name="match_793210.txt", file_path=test_dir)
        json_match = get_local_response(file_name="match_details_json_793210.txt", file_path=test_dir)
        json_comments = get_local_response(file_name="comments_json_793210.txt", file_path=test_dir)
        team = Team.objects.create(id=116152)
        self.team_html_parser = MatchHTMLParser(website, team, json_match, json_comments)

    def test_logs(self):
        logs = self.team_html_parser.get_logs()
        correct_values = [
            # TODO
        ]

        self.assertListEqual(logs, correct_values, "Match logs could not be parsed.")

    def test_enemy_team_id(self):
        enemy_team_id = self.team_html_parser.get_enemy_team_id()
        correct_value = '151662' # TODO
        self.assertEqual(enemy_team_id, correct_value, "Enemy TeamID could not be parsed.")

    def test_comments(self):
        comments = self.team_html_parser.get_comments()
        correct_values = [
            (793210, 6245777, None, 'Könntet ihr auch unter der Woche nächste Woche?', False, 'Rifftac', 1577698),
            (793210, 6246665, None, 'Prinzipell ja, es hängt nur von unseren support und Toplaner ab', False,
             'Juergen_Krapotke', 488627),
            (793210, 6246713, None,
             'Schlagt einfach mal was für nächste Woche vor an Terminen wann es euch passt. Ich denke wir sollten da schon was finden',
             False, 'Tillter', 1489058)]

        self.assertEqual(comments, correct_values, "Comments could not be parsed.")

    def test_game_day(self):
        game_day = self.team_html_parser.get_game_day()
        correct_value = 3
        self.assertEqual(game_day, correct_value, "Game day could not be parsed.")

    def test_game_begin(self):
        game_begin = self.team_html_parser.get_game_begin()
        correct_value = ""  # TODO
        self.assertEqual(game_begin, correct_value, "Game begin could not be parsed.")

    def test_enemy_lineup(self):
        enemy_lineup = self.team_html_parser.get_enemy_lineup()
        correct_values = [
            # TODO
        ]
        self.assertListEqual(enemy_lineup, correct_values, "Enemy lineup could not be parsed.")

    def test_game_closed(self):
        game_closed = self.team_html_parser.get_game_closed()
        correct_value = ""  # TODO
        self.assertEqual(game_closed, correct_value, "Game closed could not be parsed.")

    def test_game_result(self):
        game_result = self.team_html_parser.get_game_result()
        correct_value = ""  # TODO
        self.assertEqual(game_result, correct_value, "Game result could not be parsed.")

    def test_latest_suggestion(self):
        latest_suggestion = self.team_html_parser.get_latest_suggestion()
        correct_value = ""  # TODO
        self.assertEqual(latest_suggestion, correct_value, "Latest suggestion could not be parsed.")

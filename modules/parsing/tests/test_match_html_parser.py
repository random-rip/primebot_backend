import datetime
import os

import pytz
from django.conf import settings
from django.test import TestCase

from app_prime_league.models import Team
from modules.data_crawling import get_local_response
from modules.parsing.parser import MatchHTMLParser, LogPlayed, LogLineupSubmit, LogSchedulingConfirmation, LogSuggestion


class MatchHTMLParserTests(TestCase):

    def setUp(self):
        test_dir = os.path.join(settings.BASE_DIR, "parsing", "tests")
        website = get_local_response(file_name="match_793210.txt", file_path=test_dir)
        json_match = get_local_response(file_name="match_details_json_793210.txt", file_path=test_dir)
        json_comments = get_local_response(file_name="comments_json_793210.txt", file_path=test_dir)
        team = Team.objects.create(id=116152)
        self.team_html_parser = MatchHTMLParser(website, json_match, json_comments, team, )

    def assertEqualListTypes(self, actual, expected, msg):
        self.assertEqual(type(actual), list, "Actual value is not of type list.")
        self.assertEqual(type(expected), list, "Expected value is not of type list.")
        self.assertEqual(len(actual), len(expected), "Actual and expected values have not the same length.")
        for a, e in zip(actual, expected):
            self.assertEqual(type(a), e, msg=msg)

    def test_logs(self):
        logs = self.team_html_parser.get_logs()
        expected = [
            LogPlayed,
            LogLineupSubmit,
            LogSchedulingConfirmation,
            LogLineupSubmit,
            LogSuggestion,
            LogSuggestion,
            LogSuggestion,
            LogSuggestion,
        ]
        self.assertEqualListTypes(logs, expected, "Log type differs from expected type.")

    def test_enemy_team_id(self):
        enemy_team_id = self.team_html_parser.get_enemy_team_id()
        expected = '151662'
        self.assertEqual(enemy_team_id, expected, "Enemy TeamID could not be parsed.")

    def test_comments(self):
        comments = self.team_html_parser.get_comments()
        expected = [
            (793210, 6245777, None, 'Könntet ihr auch unter der Woche nächste Woche?', False, 'Rifftac', 1577698),
            (793210, 6246665, None, 'Prinzipell ja, es hängt nur von unseren support und Toplaner ab', False,
             'Juergen_Krapotke', 488627),
            (793210, 6246713, None,
             'Schlagt einfach mal was für nächste Woche vor an Terminen wann es euch passt. Ich denke wir sollten da schon was finden',
             False, 'Tillter', 1489058)]

        self.assertEqual(comments, expected, "Comments could not be parsed.")

    def test_game_day(self):
        game_day = self.team_html_parser.get_game_day()
        expected = 3
        self.assertEqual(game_day, expected, "Game day could not be parsed.")

    def test_game_begin(self):
        game_begin, log = self.team_html_parser.get_game_begin()
        expected = datetime.datetime(2021, 6, 27, 13, 0, tzinfo=pytz.UTC)
        self.assertEqual(game_begin, expected, "Game begin could not be parsed.")

    def test_enemy_lineup(self):
        enemy_lineup = self.team_html_parser.get_enemy_lineup()
        expected = [
            (1266925, 'Fronkey', 'Shennola', None),
            (488627, 'Juergen_Krapotke', 'Jürgen Krapotke', None),
            (1793322, 'MrTimTim7', 'MrTimTim', None),
            (487939, 'snprobin', 'Disperion', None),
            (1489058, 'Tillter', 'Tillter', None)
        ]
        self.assertListEqual(enemy_lineup, expected, "Enemy lineup could not be parsed.")

    def test_game_closed(self):
        game_closed = self.team_html_parser.get_game_closed()
        expected = True
        self.assertEqual(game_closed, expected, "Game closed could not be parsed.")

    def test_game_result(self):
        game_result = self.team_html_parser.get_game_result()
        expected = "1:1"
        self.assertEqual(game_result, expected, "Game result could not be parsed.")

    def test_latest_suggestion(self):
        latest_suggestion = self.team_html_parser.get_latest_suggestion()
        expected_user = "Tillter"
        expected_details = [
            datetime.datetime(2021, 6, 27, 15, 0, tzinfo=pytz.UTC),
            datetime.datetime(2021, 6, 27, 13, 0, tzinfo=pytz.UTC)
        ]
        self.assertEqual(latest_suggestion.user_id, expected_user, "User of latest suggestion is not correct.")
        self.assertEqual(latest_suggestion.details, expected_details, "Details of latest suggestion are not correct.")

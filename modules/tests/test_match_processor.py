import json
from unittest.mock import patch

from django.test import TestCase

from modules.processors.match_processor import MatchDataProcessor
from modules.providers.prime_league import PrimeLeagueProvider
from modules.tests.test_utils import string_to_datetime


class MatchProcessorTest(TestCase):

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_match_begin(self, get_match):
        get_match.return_value = json.loads('{"match": {"match_time": 1633266000}}')

        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_begin(), string_to_datetime("2021-10-03 15:00"))

    # TODO janek <3
    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_more(self, get_match):
        get_match.return_value = json.loads('{"match": {"match_time": 1633266000}}')

        processor = MatchDataProcessor(1, 1)
        print(processor.data)
        print(processor.get_match_begin())
        print(string_to_datetime("2021-10-03 15:00"))

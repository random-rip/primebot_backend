from datetime import datetime
from unittest.mock import patch

import pytz
from django.test import TestCase

from core.processors.match_processor import MatchDataProcessor
from core.providers.prime_league import PrimeLeagueProvider
from core.test_utils import string_to_datetime


class MatchBeginTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_empty(self, get_match):
        get_match.return_value = {"match": {"match_time": None}}
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_match_begin())

        get_match.return_value = {}
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_match_begin())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_timestamp(self, get_match):
        get_match.return_value = {"match": {"match_time": 1633266000}}

        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_begin(), string_to_datetime("2021-10-03 15:00"))


class MatchEnemyLineupTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_enemy_lineup(self, get_match):
        get_match.return_value = {
            "lineups": [
                {
                    "team_id": 1,
                    "user_id": 1,
                    "user_name": "Grayknife",
                    "account_value": "Grayknife",
                },
                {
                    "team_id": 2,
                    "user_id": 2,
                    "user_name": "One Enemy",
                    "account_value": "One Enemy",
                },
                {
                    "team_id": 2,
                    "user_id": 3,
                    "user_name": "Another Enemy",
                    "account_value": "Another Enemy",
                },
            ],
        }

        processor = MatchDataProcessor(match_id=1, team_id=1)
        expected = [
            (2, "One Enemy", "One Enemy", None),
            (3, "Another Enemy", "Another Enemy", None),
        ]
        self.assertListEqual(processor.get_enemy_lineup(), expected)


class MatchClosedTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_valid_values(self, get_match):
        get_match.return_value = {"match": {"match_status": "upcoming"}}
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_closed(),
        )
        get_match.return_value = {"match": {"match_status": "pending"}}
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_closed(),
        )
        get_match.return_value = {"match": {"match_status": "finished"}}
        processor = MatchDataProcessor(1, 1)
        self.assertTrue(
            processor.get_match_closed(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_unknown_values(self, get_match):
        get_match.return_value = {"match": {"match_status": "an unknown string"}}
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_closed(),
        )

        get_match.return_value = {"match": {"match_status": None}}
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_closed(),
        )


class MatchResultTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_empty(self, get_match):
        get_match.return_value = {"match": {"team_id_1": 1, "match_score_1": None, "match_score_2": None}}
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_match_result())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_win(self, get_match):
        get_match.return_value = {"match": {"team_id_1": 1, "match_score_1": 2, "match_score_2": 0}}
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_result(), "2:0")

        get_match.return_value = {"match": {"team_id_1": 2, "match_score_1": 0, "match_score_2": 2}}
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_result(), "2:0")

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_lose(self, get_match):
        get_match.return_value = {"match": {"team_id_1": 2, "match_score_1": 2, "match_score_2": 0}}
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_result(), "0:2")

        get_match.return_value = {"match": {"team_id_1": 1, "match_score_1": 0, "match_score_2": 2}}
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_result(), "0:2")

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_draw(self, get_match):
        get_match.return_value = {"match": {"team_id_1": 1, "match_score_1": 1, "match_score_2": 1}}
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(processor.get_match_result(), "1:1")


class LatestSuggestionsTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_empty(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_suggest_0": None,
                "match_scheduling_suggest_1": None,
                "match_scheduling_suggest_2": None,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(processor.get_latest_suggestions(), [])

        get_match.return_value = {"match": {}}
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(processor.get_latest_suggestions(), [])

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_one_suggestion(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_suggest_0": 1643040000,
                "match_scheduling_suggest_1": None,
                "match_scheduling_suggest_2": None,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(processor.get_latest_suggestions(), [string_to_datetime("2022-01-24 17:00")])

        get_match.return_value = {
            "match": {
                "match_scheduling_suggest_0": 1643040000,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(processor.get_latest_suggestions(), [string_to_datetime("2022-01-24 17:00")])

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_multiple_suggestions(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_suggest_0": 1643040000,
                "match_scheduling_suggest_1": 1643032800,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(
            processor.get_latest_suggestions(),
            [
                string_to_datetime("2022-01-24 17:00"),
                string_to_datetime("2022-01-24 15:00"),
            ],
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_multiple_suggestions_but_first_empty(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_suggest_0": None,
                "match_scheduling_suggest_1": 1643040000,
                "match_scheduling_suggest_2": 1643032800,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertListEqual(
            processor.get_latest_suggestions(),
            [
                string_to_datetime("2022-01-24 17:00"),
                string_to_datetime("2022-01-24 15:00"),
            ],
        )


class TeamMadeLatestSuggestionTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_empty(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 1,
                "match_scheduling_status": 0,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(
            processor.get_team_made_latest_suggestion(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_team_made_suggestion(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 1,
                "match_scheduling_status": 1,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertTrue(processor.get_team_made_latest_suggestion())

        get_match.return_value = {
            "match": {
                "team_id_2": 2,
                "match_scheduling_status": 2,
            }
        }
        processor = MatchDataProcessor(1, 2)
        self.assertTrue(processor.get_team_made_latest_suggestion())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_get_team_made_suggestion_false(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 1,
                "match_scheduling_status": 2,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(processor.get_team_made_latest_suggestion())

        get_match.return_value = {
            "match": {
                "team_id_1": 2,
                "match_scheduling_status": 1,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_team_made_latest_suggestion(),
        )


class MatchBeginConfirmedTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_empty(self, get_match):
        get_match.return_value = {}
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(processor.get_match_begin_confirmed())
        get_match.return_value = {
            "match": {
                "match_scheduling_time": None,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_begin_confirmed(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_0(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 0,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertTrue(processor.get_match_begin_confirmed())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_timestamp(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 1643040000,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertFalse(
            processor.get_match_begin_confirmed(),
        )


class DatetimeUntilAutoConfirmationTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_empty(self, get_match):
        get_match.return_value = {}
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_datetime_until_auto_confirmation())
        get_match.return_value = {
            "match": {
                "match_scheduling_time": None,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(
            processor.get_datetime_until_auto_confirmation(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_0(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 0,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_datetime_until_auto_confirmation())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_timestamp(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 48,
                "match_scheduling_suggest_time": 1643040000,
                "match_scheduling_mode": "regulated",
                "match_scheduling_start": 1643030000,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(
            datetime(2022, 1, 26, 16, tzinfo=pytz.utc),
            processor.get_datetime_until_auto_confirmation(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_scheduling_mode_fixed(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_mode": "fixed",
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_datetime_until_auto_confirmation())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_scheduling_start_earlier(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 48,
                "match_scheduling_suggest_time": 1643040000,
                "match_scheduling_mode": "regulated",
                "match_scheduling_start": 1642863600,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(
            datetime(2022, 1, 26, 16, tzinfo=pytz.utc),
            processor.get_datetime_until_auto_confirmation(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_scheduling_start_later(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 48,
                "match_scheduling_suggest_time": 1643040000,
                "match_scheduling_mode": "regulated",
                "match_scheduling_start": 1643209200,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertEqual(
            datetime(2022, 1, 28, 15, tzinfo=pytz.utc),
            processor.get_datetime_until_auto_confirmation(),
        )

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_no_suggestion(self, get_match):
        get_match.return_value = {
            "match": {
                "match_scheduling_time": 48,
                "match_scheduling_suggest_time": 0,
                "match_scheduling_mode": "regulated",
                "match_scheduling_start": 1642863600,
            }
        }
        processor = MatchDataProcessor(1, 1)
        self.assertIsNone(processor.get_datetime_until_auto_confirmation())
        # self.assertEqual(datetime(2022, 1, 26, 16, tzinfo=pytz.utc), processor.get_datetime_until_auto_confirmation(), )


class EnemyTeamIDTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_team_1(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 100,
                "team_id_2": 200,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertEqual(processor.get_enemy_team_id(), 200)

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_team_2(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 200,
                "team_id_2": 100,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertEqual(processor.get_enemy_team_id(), 200)

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_team_null(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": None,
                "team_id_2": 100,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_enemy_team_id())

        get_match.return_value = {
            "match": {
                "team_id_1": 100,
                "team_id_2": None,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_enemy_team_id())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_team_zero(self, get_match):
        get_match.return_value = {
            "match": {
                "team_id_1": 0,
                "team_id_2": 100,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_enemy_team_id())

        get_match.return_value = {
            "match": {
                "team_id_1": 100,
                "team_id_2": 0,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_enemy_team_id())


class MatchDayTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_empty(self, get_match):
        get_match.return_value = {
            "match": {
                "match_playday": None,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_match_day())

        get_match.return_value = {"match": {}}
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_match_day())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_valid(self, get_match):
        get_match.return_value = {
            "match": {
                "match_playday": 1,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertEqual(processor.get_match_day(), 1)


class LatestMatchBeginLogTest(TestCase):
    databases = []

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_empty(self, get_match):
        get_match.return_value = {
            "match": {
                "match_playday": None,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_match_day())

        get_match.return_value = {"match": {}}
        processor = MatchDataProcessor(1, 100)
        self.assertIsNone(processor.get_match_day())

    @patch.object(PrimeLeagueProvider, 'get_match')
    def test_valid(self, get_match):
        get_match.return_value = {
            "match": {
                "match_playday": 1,
            }
        }
        processor = MatchDataProcessor(1, 100)
        self.assertEqual(processor.get_match_day(), 1)

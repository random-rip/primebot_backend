from datetime import datetime
from unittest import skip

from django.test import TestCase
from django.utils import translation

from utils.utils import convert_seconds_to_hh_mm, diff_to_hh_mm, format_time_left


class DatetimeDiffTest(TestCase):
    databases = []

    def test_none(self):
        with self.assertRaises(TypeError):
            diff_to_hh_mm(datetime(2022, 1, 1, 15, 17), None)

    def test_convert_seconds_to_hh_mm(
        self,
    ):
        self.assertEqual((0, 1), convert_seconds_to_hh_mm(60))
        self.assertEqual((1, 0), convert_seconds_to_hh_mm(60 * 60))
        self.assertEqual((24, 0), convert_seconds_to_hh_mm(60 * 60 * 24))
        self.assertEqual((48, 0), convert_seconds_to_hh_mm(60 * 60 * 48))
        self.assertEqual((2, 46), convert_seconds_to_hh_mm(10_000))

    def test_diff_to_hh_mm(self):
        self.assertEqual((0, 1), diff_to_hh_mm(datetime(2022, 1, 1, 15, 17), datetime(2022, 1, 1, 15, 18)))
        self.assertEqual((1, 1), diff_to_hh_mm(datetime(2022, 1, 1, 15, 17), datetime(2022, 1, 1, 16, 18)))
        self.assertEqual((25, 0), diff_to_hh_mm(datetime(2022, 1, 1, 15, 17), datetime(2022, 1, 2, 16, 17)))

    @skip("I18n does not work :(")
    def test_formatting(self):
        self.assertEqual("0 hrs 0 min", format_time_left(0, 0))
        self.assertEqual("0 hrs 1 min", format_time_left(0, 1))
        self.assertEqual("0 hrs 2 min", format_time_left(0, 2))
        self.assertEqual("1 hr 0 min", format_time_left(1, 0))
        self.assertEqual("2 hrs 0 min", format_time_left(2, 0))
        self.assertEqual("2 hrs 1 min", format_time_left(2, 1))
        self.assertEqual("1 hr 2 min", format_time_left(1, 2))
        self.assertEqual("2 hrs 2 min", format_time_left(2, 2))
        with translation.override("de"):
            self.assertEqual("0 Std 0 Min", format_time_left(0, 0))
            self.assertEqual("0 Std 1 Min", format_time_left(0, 1))
            self.assertEqual("0 Std 2 Min", format_time_left(0, 2))
            self.assertEqual("1 Std 0 Min", format_time_left(1, 0))
            self.assertEqual("2 Std 0 Min", format_time_left(2, 0))
            self.assertEqual("2 Std 1 Min", format_time_left(2, 1))
            self.assertEqual("1 Std 2 Min", format_time_left(1, 2))
            self.assertEqual("2 Std 2 Min", format_time_left(2, 2))

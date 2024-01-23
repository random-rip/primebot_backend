from datetime import datetime

from django.test import TestCase

from app_prime_league.models import Champion


class BannedChampionsTest(TestCase):
    def test_by_banned(self):
        Champion.objects.create(name="A", banned=True, banned_until_patch="11.1")
        Champion.objects.create(name="B", banned=False, banned_until_patch="11.1")

        self.assertListEqual(["A"], list(Champion.objects.get_banned_champions().values_list("name", flat=True)))

    def test_by_banned_until(self):
        Champion.objects.create(name="A", banned=True, banned_until_patch="11.1", banned_until=datetime(2022, 1, 1))
        Champion.objects.create(name="B", banned=True, banned_until_patch="11.2", banned_until=datetime(2022, 2, 1))
        Champion.objects.create(name="C", banned=True, banned_until_patch="11.3", banned_until=datetime(2022, 3, 1))
        Champion.objects.create(name="D", banned=True, banned_until_patch="11.4", banned_until=datetime(2022, 4, 1))
        Champion.objects.create(name="E", banned=True, banned_until_patch="11.5", banned_until=datetime(2022, 5, 1))

        self.assertListEqual(
            ["D", "E"], list(Champion.objects.get_banned_champions(datetime(2022, 3, 1)).values_list("name", flat=True))
        )
        self.assertListEqual(
            ["E"], list(Champion.objects.get_banned_champions(datetime(2022, 4, 1)).values_list("name", flat=True))
        )
        self.assertListEqual(
            [], list(Champion.objects.get_banned_champions(datetime(2022, 5, 1)).values_list("name", flat=True))
        )

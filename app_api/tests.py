from django.urls import reverse
from rest_framework.test import APITestCase

from app_prime_league.models import Team, Match


class TeamTests(APITestCase):
    def setUp(self) -> None:
        Team.objects.create(id=1, name='TestTeam1', team_tag='TT1')
        Team.objects.create(id=2, name='TestTeam2', team_tag='TT2')

    def test_team_detail(self):
        url = reverse('team-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'TestTeam1')

    def test_team_list(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['team_tag'], 'TT1')
        self.assertEqual(response.data[1]['team_tag'], 'TT2')

    def test_team_detail_read_only(self):
        url = reverse('team-detail', args=(1,))
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

    def test_team_list_read_only(self):
        url = reverse('team-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class MatchTests(APITestCase):
    def setUp(self) -> None:
        Team.objects.create(id=1, name='TestTeam1', team_tag='TT1')
        Team.objects.create(id=2, name='TestTeam2', team_tag='TT2')
        Match.objects.create(id=1, match_id=1, team=Team.objects.get(pk=1), enemy_team=Team.objects.get(pk=2),
                             result='1:0', has_side_choice=0)
        Match.objects.create(id=2, match_id=2, team=Team.objects.get(pk=1), enemy_team=Team.objects.get(pk=2),
                             result='2:0', has_side_choice=0)

    def test_match_detail(self):
        url = reverse('match-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], '1:0')

    def test_match_list(self):
        url = reverse('match-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['result'], '1:0')
        self.assertEqual(response.data[1]['result'], '2:0')

    def test_match_detail_read_only(self):
        url = reverse('match-detail', args=(1,))
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

    def test_match_list_read_only(self):
        url = reverse('match-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class RouteTest(APITestCase):
    def test_api_root(self):
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

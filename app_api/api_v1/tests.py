from django.urls import reverse
from rest_framework.test import APITestCase

from app_prime_league.models import Match, Team


class TeamTests(APITestCase):
    def setUp(self) -> None:
        Team.objects.create(id=1, name='TestTeam1', team_tag='TT1')
        Team.objects.create(id=2, name='TestTeam2', team_tag='TT2')

    def test_team_detail(self):
        url = reverse('v1:team-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'TestTeam1')

    def test_team_list(self):
        url = reverse('v1:team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]['team_tag'], 'TT1')
        self.assertEqual(response.data["results"][1]['team_tag'], 'TT2')

    def test_team_detail_read_only(self):
        url = reverse('v1:team-detail', args=(1,))
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

    def test_team_list_read_only(self):
        url = reverse('v1:team-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)


class MatchTests(APITestCase):
    def setUp(self) -> None:
        self.team1 = Team.objects.create(id=1, name='TestTeam1', team_tag='TT1')
        self.team2 = Team.objects.create(id=2, name='TestTeam2', team_tag='TT2')

    def test_match_detail(self):
        match = Match.objects.create(
            match_id=1,
            team=self.team1,
            enemy_team=self.team2,
            result='1:0',
            has_side_choice=0,
        )
        url = reverse('v1:match-detail', args=(match.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], '1:0')

    def test_match_detail_by_match_id(self):
        Match.objects.create(
            match_id=1,
            team=self.team1,
            enemy_team=self.team2,
            result='1:0',
            has_side_choice=0,
        )
        match = Match.objects.create(
            match_id=1,
            team=self.team2,
            enemy_team=self.team1,
            result='0:1',
            has_side_choice=1,
        )
        url = reverse('v1:match-by-match-id')
        response = self.client.get(
            url,
            data={
                "team_id": match.team_id,
                "match_id": match.match_id,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['result'], '0:1')

    def test_match_list(self):
        Match.objects.create(
            match_id=1,
            team=self.team1,
            enemy_team=self.team2,
            result='1:0',
            has_side_choice=0,
        )
        Match.objects.create(
            match_id=2,
            team=self.team1,
            enemy_team=self.team2,
            result='2:0',
            has_side_choice=0,
        )
        url = reverse('v1:match-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]['result'], '1:0')
        self.assertEqual(response.data["results"][1]['result'], '2:0')

    def test_match_detail_read_only(self):
        match = Match.objects.create(
            match_id=1,
            team=self.team1,
            enemy_team=self.team2,
            result='1:0',
            has_side_choice=0,
        )

        url = reverse('v1:match-detail', args=(match.pk,))
        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

    def test_match_list_read_only(self):
        url = reverse('v1:match-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

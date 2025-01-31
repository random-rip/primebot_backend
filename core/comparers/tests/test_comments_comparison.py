from django.test import TestCase

from app_prime_league.factories import CommentFactory, MatchFactory, PlayerFactory, TeamFactory
from core.comparers.match_comparer import NewCommentsComparer
from core.test_utils import create_temporary_comment, create_temporary_match_data


class CompareCommentsTest(TestCase):
    def setUp(self) -> None:
        self.team_a = TeamFactory(
            players=[
                PlayerFactory(id=1, name="Player 1", summoner_name="Summonername 1"),
            ]
        )
        self.team_b = TeamFactory(
            players=[
                PlayerFactory(id=10, name="Player 10", summoner_name="Summonername 10"),
            ]
        )

    def test_no_comments(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        md = create_temporary_match_data(
            team=self.team_a,
            enemy_team=self.team_b,
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "No comments, but new comments were recognized")

    def test_existing_comments(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )
        CommentFactory(comment_id=1, user_id=1, match=match)
        md = create_temporary_match_data(
            team=self.team_a, enemy_team=self.team_b, comments=[create_temporary_comment(comment_id=1, user_id=1)]
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "1 comment exists, but new comments were recognized")

    def test_new_comment_of_team(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        md = create_temporary_match_data(
            team=self.team_a, enemy_team=self.team_b, comments=[create_temporary_comment(comment_id=1, user_id=1)]
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "New comment of members, but not recognized")

    def test_new_comment_of_enemy_team(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        md = create_temporary_match_data(
            team=self.team_a, enemy_team=self.team_b, comments=[create_temporary_comment(comment_id=10, user_id=10)]
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertListEqual(cp.compare(), [10], "New comment, but not recognized")

    def test_new_comment_of_random_user_id(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        md = create_temporary_match_data(
            team=self.team_a, enemy_team=self.team_b, comments=[create_temporary_comment(comment_id=100, user_id=100)]
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertListEqual(cp.compare(), [100], "New comment, but not recognized")

    def test_deleted_comment_of_team(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        CommentFactory(comment_id=1, user_id=1, match=match)
        md = create_temporary_match_data(team=self.team_a, enemy_team=self.team_b, comments=[])
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "No comment, but not recognized")

    def test_deleted_comment_of_enemy_team(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )
        CommentFactory(comment_id=10, user_id=10, match=match)
        md = create_temporary_match_data(team=self.team_a, enemy_team=self.team_b, comments=[])
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "No comment, but not recognized")

    def test_deleted_comment_of_random_user_id(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        CommentFactory(comment_id=100, user_id=100, match=match)
        md = create_temporary_match_data(team=self.team_a, enemy_team=self.team_b, comments=[])
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "No comment, but not recognized")

    def test_multiple_new_comments(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        md = create_temporary_match_data(
            team=self.team_a,
            enemy_team=self.team_b,
            comments=[
                create_temporary_comment(comment_id=1, user_id=1),
                create_temporary_comment(comment_id=100, user_id=100),
                create_temporary_comment(comment_id=10, user_id=10),
            ],
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertListEqual(cp.compare(), [10, 100], "Expected 2 new comments")

    def test_multiple_deletions(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        CommentFactory(comment_id=1, user_id=1, match=match)
        CommentFactory(comment_id=101, user_id=100, match=match)
        CommentFactory(comment_id=100, user_id=100, match=match)
        CommentFactory(comment_id=10, user_id=10, match=match)
        CommentFactory(comment_id=11, user_id=10, match=match)
        md = create_temporary_match_data(
            team=self.team_a,
            enemy_team=self.team_b,
            comments=[
                create_temporary_comment(comment_id=1, user_id=1),
                create_temporary_comment(comment_id=100, user_id=100),
                create_temporary_comment(comment_id=10, user_id=10),
            ],
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertFalse(cp.compare(), "No new comments expected")

    def test_multiple_adds_and_deletions(self):
        match = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )

        CommentFactory(comment_id=1, user_id=1, match=match)
        CommentFactory(comment_id=10, user_id=10, match=match)

        md = create_temporary_match_data(
            team=self.team_a,
            enemy_team=self.team_b,
            comments=[
                create_temporary_comment(comment_id=10, user_id=10),
                create_temporary_comment(comment_id=2, user_id=1),
                create_temporary_comment(comment_id=11, user_id=10),
                create_temporary_comment(comment_id=100, user_id=100),
                create_temporary_comment(comment_id=2, user_id=1),
            ],
        )
        cp = NewCommentsComparer(match=match, tmd=md)
        self.assertListEqual(cp.compare(), [11, 100], "1 new comment expected")

    def test_2_registered_teams_of_match(self):
        match1 = MatchFactory(
            team=self.team_a,
            enemy_team=self.team_b,
        )
        match2 = MatchFactory(
            team=self.team_b,
            enemy_team=self.team_a,
        )

        md = create_temporary_match_data(
            team=self.team_a,
            enemy_team=self.team_b,
            comments=[
                create_temporary_comment(comment_id=1, user_id=1),
                create_temporary_comment(comment_id=10, user_id=10),
            ],
        )
        cp = NewCommentsComparer(match=match1, tmd=md)
        self.assertListEqual(cp.compare(), [10], "1 new comment expected")

        cp.update()

        cp = NewCommentsComparer(match=match2, tmd=md)
        self.assertListEqual(cp.compare(), [1], "1 new comment expected")

        cp.update()

        cp = NewCommentsComparer(match=match1, tmd=md)
        self.assertFalse(cp.compare(), "No comment expected")

import logging
from abc import abstractmethod
from typing import Union

from app_prime_league.models import Comment, Match, Player, Suggestion, Team
from bots.discord_interface.create_event import CreateDiscordEventJob
from bots.message_dispatcher.creator import MessageCreatorJob
from bots.messages import (
    EnemyNewTimeSuggestionsNotificationMessage,
    NewCommentsNotificationMessage,
    NewLineupNotificationMessage,
    OwnNewTimeSuggestionsNotificationMessage,
    ScheduleConfirmationNotification,
)
from core.processors.team_processor import TeamDataProcessor
from core.providers.get import get_provider
from core.temporary_match_data import TemporaryMatchData

notifications_logger = logging.getLogger("notifications")


class Comparer:
    def __init__(self, match: Match, tmd: TemporaryMatchData):
        self.match = match
        self.tmd = tmd
        self.log_message = f"New notification for {match=} ({match.team=}): "

    @abstractmethod
    def compare(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def notify(self):
        pass

    def log(self, msg):
        notifications_logger.info(f"{self.log_message}{msg}")


class NewSuggestionComparer(Comparer):
    def __init__(self, match: Match, tmd: TemporaryMatchData, of_enemy_team: bool):
        super().__init__(match, tmd)
        self.of_enemy_team = of_enemy_team

    def compare(self):
        """
        Comparing the latest suggestions of match_old and match_new and returns True if a new suggestion was made.
        If of_enemy_team is True, checks if the new suggestion was made by the enemy team.
        :param of_enemy_team:
        :return boolean: True if new suggestion else False
        """
        if (
            self.tmd.team_made_latest_suggestion is None
            or self.match.team_made_latest_suggestion == self.tmd.team_made_latest_suggestion
        ):
            return False
        if self.of_enemy_team and not self.tmd.team_made_latest_suggestion:
            return True
        if not self.of_enemy_team and self.tmd.team_made_latest_suggestion:
            return True
        return False

    def update(self):
        if self.tmd.latest_suggestions is not None:
            self.match.suggestion_set.all().delete()
            for suggestion in self.tmd.latest_suggestions:
                self.match.suggestion_set.add(Suggestion(match=self.match, begin=suggestion), bulk=False)
        self.match.team_made_latest_suggestion = self.tmd.team_made_latest_suggestion

    def notify(self):
        if self.of_enemy_team:
            log_msg = "Neuer Terminvorschlag der Gegner"
            msg_class = EnemyNewTimeSuggestionsNotificationMessage
        else:
            log_msg = "Eigener neuer Terminvorschlag"
            msg_class = OwnNewTimeSuggestionsNotificationMessage
        self.log(log_msg)
        MessageCreatorJob(msg_class=msg_class, team=self.match.team, match=self.match).enqueue()


class SchedulingConfirmationComparer(Comparer):
    def compare(self):
        return not self.match.match_begin_confirmed and self.tmd.match_begin_confirmed

    def update(self):
        self.match.begin = self.tmd.begin
        self.match.match_begin_confirmed = self.tmd.match_begin_confirmed
        self.match.datetime_until_auto_confirmation = self.tmd.datetime_until_auto_confirmation

    def notify(self):
        self.log("Termin wurde festgelegt")
        MessageCreatorJob(
            msg_class=ScheduleConfirmationNotification,
            team=self.match.team,
            match=self.match,
            latest_confirmation_log=self.tmd.latest_confirmation_log,
        ).enqueue()
        if self.match.team.discord_channel_id is not None and self.match.team.value_of_setting(
            "CREATE_DISCORD_EVENT_ON_SCHEDULING_CONFIRMATION", default=False
        ):
            CreateDiscordEventJob(self.match).enqueue()


class LineupConfirmationComparer(Comparer):
    def __init__(self, match: Match, tmd: TemporaryMatchData, of_enemy_team: bool):
        super().__init__(match, tmd)
        self.of_enemy_team = of_enemy_team

    def compare(self):
        new_lineup = self.tmd.enemy_lineup if self.of_enemy_team else self.tmd.team_lineup
        if new_lineup is None:
            return False
        old_lineup = self.match.enemy_lineup if self.of_enemy_team else self.match.team_lineup
        old_lineup = list(old_lineup.all().values_list("id", flat=True))
        for user_id, *_ in new_lineup:
            if user_id in old_lineup:
                continue
            else:
                return True
        return False

    def update(self):
        if self.of_enemy_team and self.tmd.enemy_lineup is not None:
            self.match.enemy_lineup.clear()
            players = Player.objects.create_or_update_players(self.tmd.enemy_lineup, team=self.match.enemy_team)
            self.match.enemy_lineup.add(*players)
            return
        if not self.of_enemy_team and self.tmd.team_lineup is not None:
            self.match.team_lineup.clear()
            players = Player.objects.create_or_update_players(self.tmd.team_lineup, team=self.match.team)
            self.match.team_lineup.add(*players)

    def notify(self):
        if self.of_enemy_team:
            self.log("Neues Lineup des gegnerischen Teams")
            MessageCreatorJob(
                msg_class=NewLineupNotificationMessage,
                team=self.match.team,
                match=self.match,
            ).enqueue()
        else:
            self.log("SILENCED Neues Lineup des eigenen Teams")


class NewCommentsComparer(Comparer):
    def __init__(self, match: Match, tmd: TemporaryMatchData):
        super().__init__(match, tmd)
        self._new_ids = None

    def compare(self):
        """
        Check if new comments occurred which are not from team members.
        The list is sorted by comment_ids ascending.
        Returns: List of integers or False
        """
        user_ids_of_team = self.match.team.player_set.all().values_list("id", flat=True)
        old_comment_ids_without_team_comments = set(
            self.match.comment_set.exclude(user_id__in=user_ids_of_team).values_list("comment_id", flat=True)
        )
        new_comment_ids_without_team_comments = set(
            [x.comment_id for x in self.tmd.comments if x.user_id not in user_ids_of_team]
        )
        self._new_ids = sorted(list(new_comment_ids_without_team_comments - old_comment_ids_without_team_comments))
        return self._new_ids or False

    def update(self):
        for i in self.tmd.comments:
            Comment.objects.update_or_create(
                match=self.match, comment_id=i.comment_id, defaults={**i.comment_as_dict()}
            )

    def notify(self):
        self.log(f"Neue Kommentare: {self._new_ids}")
        MessageCreatorJob(
            msg_class=NewCommentsNotificationMessage,
            team=self.match.team,
            match=self.match,
            new_comment_ids=self._new_ids,
        ).enqueue()


class NewEnemyTeamComparer(Comparer):
    def __init__(self, match: Match, tmd: TemporaryMatchData, priority: int):
        super().__init__(match, tmd)
        self.priority = priority

    def compare(self):
        return not self.tmd.enemy_team_id == self.match.enemy_team_id

    def update(self):
        processor = TeamDataProcessor(
            team_id=self.tmd.enemy_team_id,
            provider=get_provider(priority=self.priority),
        )
        enemy_team, created = Team.objects.update_or_create(
            id=self.tmd.enemy_team_id,
            defaults={
                "name": processor.get_team_name(),
                "team_tag": processor.get_team_tag(),
                "division": processor.get_current_division(),
                "split": processor.get_split(),
            },
        )
        self.match.enemy_team = enemy_team
        Player.objects.remove_old_player_relations(processor.get_members(), self.match.team)
        Player.objects.create_or_update_players(processor.get_members(), enemy_team)

    def notify(self):
        pass


class MatchComparer:
    def __init__(self, match: Union[Match,], tmd: TemporaryMatchData, comparers: list[Comparer]):
        self.match = match
        self.tmd = tmd
        self.comparers = comparers
        self.triggered_comparers = []

    def run(self):
        for comparer in self.comparers:
            if comparer.compare():
                self.triggered_comparers.append(comparer)

    def update(self):
        for comparer in self.triggered_comparers:
            comparer.update()

        self.match.match_id = self.tmd.match_id
        self.match.match_day = self.tmd.match_day
        self.match.match_type = self.tmd.match_type
        self.match.team = self.tmd.team
        self.match.begin = self.tmd.begin  # these lines should be updated in the dedicated comparers if necessary
        self.match.match_begin_confirmed = self.tmd.match_begin_confirmed
        self.match.datetime_until_auto_confirmation = self.tmd.datetime_until_auto_confirmation
        self.match.closed = self.tmd.closed
        self.match.result = self.tmd.result
        self.match.has_side_choice = self.tmd.has_side_choice
        self.match.split = self.tmd.split
        self.match.save()

    def notify(self):
        for comparer in self.triggered_comparers:
            comparer.notify()

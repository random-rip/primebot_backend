import logging
from typing import List

from django.db import IntegrityError, models

update_logger = logging.getLogger("updates")


class PlayerManager(models.Manager):
    def remove_old_player_relations(self, players_list: list, team: "Team"):  # noqa
        current_account_ids = [account_id for account_id, *_ in players_list]
        for player in team.player_set.all():
            if player.id in current_account_ids:
                continue
            player.team = None
            player.save()

    def create_or_update_players(self, players_list: list, team: "Team") -> List["Player"]:  # noqa
        current_players = []
        for (
            account_id,
            name,
            summoner_name,
            is_leader,
        ) in players_list:
            if any([name is None, summoner_name is None]):
                continue
            to_update = {"name": name, "summoner_name": summoner_name, "is_leader": is_leader or False, "team": team}
            try:
                player = self.model.objects.get(id=account_id, **to_update)
            except self.model.DoesNotExist:
                try:
                    player, _ = self.model.objects.update_or_create(id=account_id, defaults=to_update)
                    update_logger.info(f"Updated player {player.name} ({player.id})")
                except IntegrityError:
                    update_logger.warning(f"Cannot update player {to_update}. Missing values.")
                    continue
            current_players.append(player)
        return current_players

    def get_active_players(self):
        """
        Players with a missing Game-Account have no `summoner_name`.
        :return: Filtered QuerySet with active players
        """
        return self.get_queryset().filter(summoner_name__isnull=False)


class ScoutingWebsiteManager(models.Manager):
    def get_multi_websites(self):
        qs = self.model.objects.filter(multi=True).order_by("created_at")
        return qs if qs.exists() else [self.model.default()]


class CommentManager(models.Manager):
    pass


class ChampionManager(models.Manager):
    def get_banned_champions(self, until=None):
        """
        Get banned Champions based on `banned=True`. If `until` is set, only return champions that are banned until
        this date.
        :param until: optional Date
        :return: queryset
        """
        if until:
            return self.model.objects.filter(banned_until__gt=until).order_by("name")
        else:
            return self.model.objects.filter(banned=True).order_by("name")

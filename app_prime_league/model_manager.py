import logging
from datetime import timedelta

from django.db import models, IntegrityError
from django.db.models import Q
from django.utils import timezone

update_logger = logging.getLogger("updates")


class TeamManager(models.Manager):

    def get_registered_teams(self):
        """
        Gibt alle Teams zurück, die entweder in einer Telegram-Gruppe oder in einem Discord-Channel registriert wurden.
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))

    def get_registered_team_of_current_split(self):
        """
        Gibt alle Teams zurück, die entweder in einer Telegram-Gruppe oder in einem Discord-Channel registriert wurden
        und wo die Division gesetzt wurde!
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False),
                                         division__isnull=False)

    def get_team(self, team_id):
        return self.model.objects.filter(id=team_id).first()

    def get_calibration_teams(self):
        # TODO neues Feld in model
        return self.model.objects.filter(id__in=[116152, 146630, 135572, 153698])
        # return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))


class MatchManager(models.Manager):

    def get_uncompleted_matches(self):
        """
        Gibt alle Matches zurück die nicht `closed` oder `NULL` oder deren Spielbeginn länger als 2 Tage her sind.
        Returns: queryset

        """
        qs = self.model.objects.filter(
            Q(closed=False) |
            Q(closed__isnull=True) |
            Q(closed=True, begin__gte=timezone.now() - timedelta(days=2)))
        return qs

    def get_match_of_team(self, match_id, team):
        try:
            return self.model.objects.get(match_id=match_id, team=team)
        except self.model.DoesNotExist:
            return None


class PlayerManager(models.Manager):

    def create_or_update_players(self, players_list: list, team):
        players = []
        for (account_id, name, summoner_name, is_leader,) in players_list:
            to_update = {
                "name": name,
                "summoner_name": summoner_name,
                "is_leader": is_leader or False,
                "team": team
            }
            try:
                player = self.model.objects.get(id=account_id, **to_update)
            except self.model.DoesNotExist:
                try:
                    player, _ = self.model.objects.update_or_create(id=account_id, defaults=to_update)
                    update_logger.info(f"Updated {player.name} ({player.id})")
                except IntegrityError:
                    update_logger.warning(
                        f"Exception occurred while updating player {to_update}"
                    )
                    continue
            players.append(player)
        return players

    def get_active_players(self):
        """
        Spieler mit fehlendem Gameaccount haben keinen `summoner_name`.
        Returns: aktive Spieler

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

        Args:
            until: optional Datetime

        Returns:

        """
        qs = self.model.objects.filter(banned=True, ).order_by("name")
        return qs if not until else qs.filter(banned_until__gt=until)

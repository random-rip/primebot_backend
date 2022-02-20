from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone


class TeamManager(models.Manager):

    def get_watched_teams(self):
        """
        Gibt alle Teams zurück, die entweder in einer Telegram-Gruppe oder in einem Discord-Channel registriert wurden.
        :return: Queryset of Team Model
        """
        return self.model.objects.filter(Q(telegram_id__isnull=False) | Q(discord_channel_id__isnull=False))

    def get_watched_team_of_current_split(self):
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
        for (_id, name, summoner_name, is_leader,) in players_list:
            player, _ = self.model.objects.update_or_create(id=_id, defaults={
                "name": name,
                "team": team,
                "summoner_name": summoner_name,
                "is_leader": is_leader or False,
            })
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
        return self.model.objects.filter(multi=True).order_by("created_at")


class CommentManager(models.Manager):
    pass

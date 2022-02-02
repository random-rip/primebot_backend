from django.db import models
from django.db.models import Q


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
        return self.model.objects.filter(Q(closed=False) | Q(closed__isnull=True))

    def get_match_of_team(self, match_id, team):
        try:
            return self.model.objects.get(match_id=match_id, team=team)
        except self.model.DoesNotExist:
            return None


class PlayerManager(models.Manager):

    def create_or_update_players(self, players_list: list, team):
        players = []
        for (id_, name, summoner_name, is_leader,) in players_list:
            player, created = self.model.objects.get_or_create(id=id_, defaults={
                "name": name,
                "team": team,
                "summoner_name": summoner_name,
                "is_leader": is_leader,
            })
            if not created:
                player.name = name
                player.team = team
                player.summoner_name = summoner_name
                if is_leader is not None:
                    player.is_leader = is_leader
                player.save()
            players.append(player)
        return players


class CommentManager(models.Manager):
    pass
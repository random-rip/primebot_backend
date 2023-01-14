from django.conf import settings
from django.db import models
from django.template.defaultfilters import urlencode

from app_prime_league.model_manager import ScoutingWebsiteManager


class ScoutingWebsite(models.Model):
    name = models.CharField(max_length=20, unique=True)
    base_url = models.CharField(max_length=200)
    separator = models.CharField(max_length=5, blank=True)
    multi = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ScoutingWebsiteManager()

    class Meta:
        db_table = "scouting_websites"
        verbose_name = "Scouting Website"
        verbose_name_plural = "Scouting Websites"

    def generate_url(self, names):
        """
        Url encode given names and generate link.
        Args:
            names:  list of strings or string

        Returns: String
        """
        if not isinstance(names, list):
            names = [names]
        names = [urlencode(x) for x in names]
        if self.multi:
            return self.base_url.format(self.separator.join(names))
        return self.base_url.format("".join(names))

    @staticmethod
    def default() -> "ScoutingWebsite":
        return ScoutingWebsite(
            name=settings.DEFAULT_SCOUTING_NAME,
            base_url=settings.DEFAULT_SCOUTING_URL,
            separator=settings.DEFAULT_SCOUTING_SEP,
            multi=True,
        )

    def __str__(self):
        return self.name

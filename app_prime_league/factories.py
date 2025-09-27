import random
from datetime import date
from zoneinfo import ZoneInfo

import factory
from factory import lazy_attribute
from factory.django import DjangoModelFactory

from .models import Channel, Comment, Match, Player, Split, Team
from .models.channel import Platforms


class SplitFactory(DjangoModelFactory):
    """
    Default:

    * Registration starts 14 days before group stage start: 11.01.2024
    * Registration ends 1 day before group stage start: 24.01.2024
    * Calibration stage starts 4 days before the registration ends: 20.01.2024
    * Calibration stage on the same day as the registration ends: 24.01.2024
    * Group stage starts on 25.01.2024
    * Group stage monday is 29.01.2024
        * 1. match day is 04.02.2024
        * 2. match day is 11.02.2024
        * 3. match day is 18.02.2024
        * 4. match day is 25.02.2024
        * 5. match day is 03.03.2024
        * 6. match day is 10.03.2024
        * 7. match day is 17.03.2024
        * 8. match day is 24.03.2024
    * Tiebreaker match week is until 31.03.2024
    * Group stage ends 9 weeks after group stage start: 31.03.2024
    * Playoffs start 1 week after group stage ends: 14.04.2024
    * Playoffs end 2 weeks after playoffs start: 29.04.2024
    """

    registration_start = date(2024, 1, 11)
    registration_end = date(2024, 1, 24)
    calibration_stage_start = date(2024, 1, 20)
    calibration_stage_end = date(2024, 1, 24)
    group_stage_start = date(2024, 1, 25)
    group_stage_start_monday = date(2024, 1, 29)
    group_stage_end = date(2024, 3, 31)
    playoffs_start = date(2024, 4, 14)
    playoffs_end = date(2024, 4, 29)

    @lazy_attribute
    def name(self):
        return f"Split {self.group_stage_start.strftime('%m %Y')}"

    class Meta:
        model = Split

    @staticmethod
    def from_registration_dates(registration_start: date, registration_end: date):
        return SplitFactory(**Split.calculate(registration_start, registration_end))


class TeamFactory(DjangoModelFactory):
    name = factory.Faker("name")
    team_tag = factory.Faker("word")
    division = factory.Faker("word")

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            return

        if type(extracted) is not list:
            extracted = [extracted]
        self.channels.set(extracted)

    @factory.post_generation
    def matches(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            return

        if type(extracted) is not list:
            extracted = [extracted]
        self.matches.set(extracted)

    @factory.post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            return

        if type(extracted) is not list:
            extracted = [extracted]
        self.player_set.set(extracted)

    class Meta:
        model = Team


class MatchFactory(DjangoModelFactory):
    match_id = factory.Faker("random_int")
    match_day = factory.LazyFunction(lambda: random.choice([0, 99] + list(range(1, 10))))
    match_type = factory.Faker(
        "word",
        ext_word_list=Match.MatchType.values,
    )
    team = factory.SubFactory(TeamFactory)
    enemy_team = factory.SubFactory(TeamFactory)

    @factory.post_generation
    def enemy_lineup(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            return

        if type(extracted) is not list:
            extracted = [extracted]
        self.enemy_lineup.set(extracted)

    class Meta:
        model = Match


class ChannelFactory(DjangoModelFactory):
    platform = factory.Faker(
        "word",
        ext_word_list=[
            Platforms.DISCORD,
            Platforms.TELEGRAM,
        ],
    )

    @factory.lazy_attribute
    def telegram_id(self):
        if self.platform == Platforms.TELEGRAM:
            return factory.Faker("random_int")
        return None

    @factory.lazy_attribute
    def discord_guild_id(self):
        if self.platform == Platforms.DISCORD:
            return factory.Faker("random_int")
        return None

    @factory.lazy_attribute
    def discord_channel_id(self):
        if self.platform == Platforms.DISCORD:
            return factory.Faker("random_int")
        return None

    @factory.lazy_attribute
    def discord_webhook_id(self):
        if self.platform == Platforms.DISCORD:
            return factory.Faker("uuid4")
        return None

    @factory.lazy_attribute
    def discord_webhook_token(self):
        if self.platform == Platforms.DISCORD:
            return factory.Faker("uuid4")
        return None

    @factory.post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            return

        if type(extracted) is not list:
            extracted = [extracted]
        self.teams.set(extracted)

    class Meta:
        model = Channel


class PlayerFactory(DjangoModelFactory):
    name = factory.Faker("name")
    team = factory.SubFactory(TeamFactory)
    summoner_name = factory.lazy_attribute(lambda o: f"{o.name}")

    class Meta:
        model = Player


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    comment_id = factory.Faker("random_int")
    comment_parent_id = factory.Faker("random_int")
    comment_time = factory.Faker("date_time", tzinfo=ZoneInfo("UTC"))
    user_id = factory.Faker("random_int")
    comment_edit_user_id = factory.Faker("random_int")
    comment_flag_staff = factory.Faker("boolean")
    comment_flag_official = factory.Faker("boolean")
    match = factory.SubFactory(MatchFactory)

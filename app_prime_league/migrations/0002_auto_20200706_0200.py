from django.db import migrations

from prime_league_bot import settings


def add_seeds(apps, schema_editor):
    Player = apps.get_model('app_prime_league', 'Player')
    admin = Player(name="System(admin)")
    admin.save()
    admin2 = Player(name="System")
    admin2.save()

    if settings.DEFAULT_TEAM_ID is not None:
        Team = apps.get_model('app_prime_league', 'Team')
        team = Team(
            id=settings.DEFAULT_TEAM_ID,
            telegram_channel_id=settings.DEFAULT_TELEGRAM_CHANNEL_ID
        )
        team.save()


class Migration(migrations.Migration):
    dependencies = [
        ('app_prime_league', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_seeds),
    ]

from django.db import migrations

from prime_league_bot import settings


def add_seeds(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('app_prime_league', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_seeds),
    ]

# Generated by Django 3.0.8 on 2021-06-02 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0013_team_discord_role_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='game_closed',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='game_day',
            field=models.IntegerField(null=True),
        ),
    ]

# Generated by Django 3.0.8 on 2020-09-19 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0008_auto_20200721_2316'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='discord_channel_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='discord_guild_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

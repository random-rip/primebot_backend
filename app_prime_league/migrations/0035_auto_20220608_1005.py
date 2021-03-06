# Generated by Django 3.0.8 on 2022-06-08 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0034_auto_20220220_2032'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Changelog',
        ),
        migrations.AlterField(
            model_name='match',
            name='enemy_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_as_enemy_team', to='app_prime_league.Team'),
        ),
        migrations.AlterField(
            model_name='team',
            name='discord_channel_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='discord_role_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='discord_webhook_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='discord_webhook_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='division',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='logo_url',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='scouting_website',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_prime_league.ScoutingWebsite'),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_tag',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='telegram_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]

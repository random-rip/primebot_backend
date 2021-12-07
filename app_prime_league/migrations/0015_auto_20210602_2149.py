# Generated by Django 3.0.8 on 2021-06-02 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0014_auto_20210602_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='enemy_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_as_enemy_team', to='app_prime_league.Team'),
        ),
    ]

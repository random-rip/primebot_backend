# Generated by Django 3.0.8 on 2020-07-05 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.IntegerField()),
                ('game_day', models.IntegerField()),
                ('game_begin', models.DateTimeField(null=True)),
                ('game_closed', models.BooleanField()),
            ],
            options={
                'db_table': 'games',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('team_tag', models.CharField(max_length=10, null=True)),
                ('division', models.CharField(max_length=5, null=True)),
                ('telegram_channel_id', models.CharField(max_length=50, null=True)),
            ],
            options={
                'db_table': 'teams',
            },
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_begin', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_prime_league.Game')),
            ],
            options={
                'db_table': 'suggestion',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('summoner_name', models.CharField(max_length=30, null=True)),
                ('is_leader', models.BooleanField(default=False)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app_prime_league.Team')),
            ],
            options={
                'db_table': 'players',
            },
        ),
        migrations.AddField(
            model_name='game',
            name='enemy_lineup',
            field=models.ManyToManyField(to='app_prime_league.Player'),
        ),
        migrations.AddField(
            model_name='game',
            name='enemy_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_as_enemy_team', to='app_prime_league.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_against', to='app_prime_league.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='game',
            unique_together={('game_id', 'team')},
        ),
    ]
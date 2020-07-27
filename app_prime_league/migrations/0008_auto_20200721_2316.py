# Generated by Django 3.0.8 on 2020-07-21 21:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0007_auto_20200718_0153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='telegram_channel_id',
            new_name='telegram_id',
        ),
        migrations.AddField(
            model_name='game',
            name='game_result',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterModelTable(
            name='suggestion',
            table='suggestions',
        ),
        migrations.CreateModel(
            name='TeamWatcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_prime_league.Team')),
            ],
            options={
                'db_table': 'watched_teams',
                'unique_together': {('telegram_id', 'team')},
            },
        ),
    ]
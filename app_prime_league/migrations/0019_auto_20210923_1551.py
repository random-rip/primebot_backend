# Generated by Django 3.0.8 on 2021-09-23 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0018_auto_20210923_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='scouting_website',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_prime_league.ScoutingWebsite'),
        ),
    ]

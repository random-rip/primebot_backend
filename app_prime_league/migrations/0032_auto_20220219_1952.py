# Generated by Django 3.0.8 on 2022-02-19 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0031_auto_20220218_2334'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scoutingwebsite',
            options={'verbose_name': 'Scouting Website', 'verbose_name_plural': 'Scouting Websites'},
        ),
        migrations.AddField(
            model_name='scoutingwebsite',
            name='multi',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='scoutingwebsite',
            name='separator',
            field=models.CharField(default=',', max_length=5, null=True),
        ),
    ]

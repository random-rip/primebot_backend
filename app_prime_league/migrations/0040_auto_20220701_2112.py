# Generated by Django 3.0.8 on 2022-07-01 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0039_merge_20220618_1453'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name': 'Match', 'verbose_name_plural': 'Matches'},
        ),
        migrations.AlterField(
            model_name='team',
            name='language',
            field=models.CharField(choices=[('de', 'german'), ('en', 'english')], default='de', max_length=2),
        ),
    ]

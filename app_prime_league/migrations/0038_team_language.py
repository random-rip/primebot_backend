# Generated by Django 3.0.8 on 2022-06-16 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_prime_league', '0037_comment_comment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='language',
            field=models.CharField(choices=[('de', 'deutsch'), ('en', 'englisch')], default='de', max_length=2),
        ),
    ]

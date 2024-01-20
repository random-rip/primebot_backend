# Generated by Django 3.2.23 on 2024-01-08 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quicklink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('help_text', models.CharField(blank=True, default='', max_length=255)),
                ('url', models.URLField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('is_internal', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('icon', models.ImageField(blank=True, help_text='Icons should be 40x40 pixels.', null=True, upload_to='quicklinks')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group')),
            ],
            options={
                'ordering': ('order', 'title'),
            },
        ),
    ]
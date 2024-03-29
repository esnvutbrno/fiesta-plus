# Generated by Django 4.2.8 on 2024-01-18 22:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0030_buddysystemconfiguration_rolling_limit_window_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddysystemconfiguration',
            name='rolling_limit',
            field=models.PositiveSmallIntegerField(default=0, help_text="Number of requests a member can match in the time rolling window. Members with reached limit in specified time-window won't be able to match another buddy request. Set to 0 to disable limit.", verbose_name='rolling limit'),
        ),
        migrations.AlterField(
            model_name='buddysystemconfiguration',
            name='rolling_limit_window',
            field=models.DurationField(default=datetime.timedelta(days=84), help_text='Time window for the rolling limit. Use format DD HH:MM:SS.', verbose_name='rolling limit time window'),
        ),
    ]

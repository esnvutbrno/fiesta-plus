# Generated by Django 4.2.8 on 2024-01-18 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_system', '0008_pickupsystemconfiguration_rolling_limit_window_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pickupsystemconfiguration',
            name='rolling_limit',
        ),
        migrations.RemoveField(
            model_name='pickupsystemconfiguration',
            name='rolling_limit_window',
        ),
    ]
# Generated by Django 4.2.7 on 2023-11-16 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0027_alter_buddysystemconfiguration_matching_policy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='buddysystemconfiguration',
            name='display_issuer_first_name',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buddysystemconfiguration',
            name='display_issuer_last_name',
            field=models.BooleanField(default=False),
        ),
    ]
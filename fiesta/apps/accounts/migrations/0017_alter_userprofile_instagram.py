# Generated by Django 4.2.4 on 2023-09-02 12:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_userprofile_facebook_userprofile_instagram_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='instagram',
            field=models.CharField(blank=True, validators=[django.core.validators.RegexValidator('^[\\w\\-_.]+$')], verbose_name='instagram username'),
        ),
    ]

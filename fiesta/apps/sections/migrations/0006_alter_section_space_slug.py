# Generated by Django 4.0.2 on 2022-07-23 18:02

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0005_alter_section_space_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='space_slug',
            field=models.SlugField(help_text='Slug used for defining section spaces as URL subdomains.', unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[a-z]+\\Z'), 'Enter a valid “slug” consisting of lowercase letters.', 'invalid')], verbose_name='space slug'),
        ),
    ]

# Generated by Django 4.2.7 on 2023-12-17 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0021_alter_sectionuniversity_section_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionsconfiguration',
            name='required_birth_date',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required birth date'),
        ),
    ]
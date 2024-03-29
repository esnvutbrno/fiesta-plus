# Generated by Django 4.2.7 on 2023-11-12 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0018_sectionsconfiguration_required_university'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_faculty',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required faculty'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_gender',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required gender'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_interests',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required interests'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_nationality',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required nationality'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_phone_number',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required phone number'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_picture',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required profile picture'),
        ),
        migrations.AlterField(
            model_name='sectionsconfiguration',
            name='required_university',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: Yes=field is required, No=field is optional, Unknown=field is not available', null=True, verbose_name='required university'),
        ),
    ]

# Generated by Django 4.1 on 2022-08-05 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0009_alter_sectionsconfiguration_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionsconfiguration',
            name='required_phone_number',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: True=is required, False=is optional, None=not available', null=True, verbose_name='required phone number'),
        ),
    ]
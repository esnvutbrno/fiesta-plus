# Generated by Django 4.2.7 on 2023-11-10 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0017_sectionsconfiguration_required_faculty'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionsconfiguration',
            name='required_university',
            field=models.BooleanField(blank=True, default=None, help_text='Flag if field is needed to fill in user profile: True=field is required, False=field is optional, None=field is not available', null=True, verbose_name='required university'),
        ),
    ]

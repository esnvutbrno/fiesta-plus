# Generated by Django 4.2.7 on 2023-11-17 14:49

from django.db import migrations, models
import location_field.models.plain


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_system', '0003_pickupsystemconfiguration_display_issuer_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickuprequest',
            name='location',
            field=location_field.models.plain.PlainLocationField(default='49.1922443,16.6113382', max_length=63, verbose_name='pickup point'),
        ),
        migrations.AlterField(
            model_name='pickuprequest',
            name='place',
            field=models.CharField(max_length=256, verbose_name='pickup place name'),
        ),
    ]

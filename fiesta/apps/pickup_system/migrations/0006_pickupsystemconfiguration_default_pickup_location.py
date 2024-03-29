# Generated by Django 4.2.7 on 2023-12-15 10:48

from django.db import migrations
import location_field.models.plain


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_system', '0005_alter_pickuprequest_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickupsystemconfiguration',
            name='default_pickup_location',
            field=location_field.models.plain.PlainLocationField(blank=True, max_length=63, null=True, verbose_name='default pickup location'),
        ),
    ]

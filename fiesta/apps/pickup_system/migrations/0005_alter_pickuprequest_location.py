# Generated by Django 4.2.7 on 2023-12-14 16:26

from django.db import migrations
import location_field.models.plain


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_system', '0004_alter_pickuprequest_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickuprequest',
            name='location',
            field=location_field.models.plain.PlainLocationField(blank=True, max_length=63, null=True, verbose_name='pickup point'),
        ),
    ]
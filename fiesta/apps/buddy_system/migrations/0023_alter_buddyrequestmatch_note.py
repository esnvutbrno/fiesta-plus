# Generated by Django 4.2.4 on 2023-10-27 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0022_alter_buddyrequestmatch_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequestmatch',
            name='note',
            field=models.TextField(blank=True, default='', verbose_name='text from matcher'),
            preserve_default=False,
        ),
    ]
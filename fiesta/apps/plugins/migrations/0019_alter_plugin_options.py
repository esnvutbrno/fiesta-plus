# Generated by Django 4.2.7 on 2023-11-27 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0018_alter_plugin_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plugin',
            options={'ordering': ('section', 'app_label'), 'verbose_name': 'plugin', 'verbose_name_plural': 'plugins'},
        ),
    ]

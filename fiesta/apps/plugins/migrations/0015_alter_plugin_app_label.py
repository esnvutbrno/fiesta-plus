# Generated by Django 4.2.4 on 2023-10-27 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plugins', '0014_alter_plugin_app_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugin',
            name='app_label',
            field=models.CharField(choices=[('buddy_system', 'Buddy System'), ('dashboard', 'Dashboard'), ('sections', 'ESN section'), ('esncards', 'ESNcard'), ('events', 'Events'), ('pages', 'Pages')], help_text='Defines system application, which specific plugin represents.', max_length=256, verbose_name='app label'),
        ),
    ]

# Generated by Django 4.1.7 on 2023-04-03 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0011_merge_20220823_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='system_state',
            field=models.CharField(choices=[('enabled', 'Enabled'), ('paused', 'Paused'), ('disabled', 'Disabled')], default='disabled', help_text='Marks state of the section in context of usage of this system.', max_length=16, verbose_name='state in this system'),
        ),
    ]

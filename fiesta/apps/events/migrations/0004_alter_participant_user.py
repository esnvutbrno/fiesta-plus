# Generated by Django 4.2.4 on 2023-10-02 13:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0003_participant_state_alter_organizer_event_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
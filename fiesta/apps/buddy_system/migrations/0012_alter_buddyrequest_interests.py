# Generated by Django 4.1 on 2022-08-05 15:35

import apps.utils.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0011_alter_buddyrequest_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequest',
            name='interests',
            field=apps.utils.models.fields.ArrayFieldWithDisplayableChoices(base_field=models.CharField(choices=[('video-making', '🎥 Video-making'), ('architecture', '🏛️️ Architecture'), ('movies', '🎞️ Movies'), ('fashion', '🧥️ Fashion'), ('dance', '💃 Dancing'), ('IT', '🧑\u200d💻 IT'), ('yoga', '🧘️ Yoga'), ('theatre', '🎭️ Theatre'), ('music', '🎶 Music'), ('photo', '📸 Photography'), ('running', '🏃\u200d♀️ Running'), ('pets', '🐕️ Pets'), ('food', '🍲 Food'), ('footbal', '⚽ Football'), ('coffee', '☕ Coffee'), ('reading', '📚️ Reading'), ('party', '🎉 Partying'), ('travel', '✈ Travelling'), ('hiking', '⛰️ Hiking'), ('tik-tok', '🤡️️ TikTok scrolling'), ('self-development', '🧑📚️ Self-development'), ('volleyball', '🏐️ Volleyball'), ('shopping', '🛍️️ Shopping')], default=None, max_length=24), blank=True, default=list, size=None, verbose_name='issuer interests'),
        ),
    ]

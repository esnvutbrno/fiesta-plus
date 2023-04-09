# Generated by Django 4.1.7 on 2023-04-03 19:37

import apps.utils.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0014_alter_buddyrequest_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequest',
            name='interests',
            field=apps.utils.models.fields.ArrayFieldWithDisplayableChoices(base_field=models.CharField(choices=[('running', '🏃\u200d♀️ Running'), ('theatre', '🎭️ Theatre'), ('yoga', '🧘️ Yoga'), ('music', '🎶 Music'), ('movies', '🎞️ Movies'), ('pets', '🐕️ Pets'), ('shopping', '🛍️️ Shopping'), ('party', '🎉 Partying'), ('travel', '✈ Travelling'), ('tik-tok', '🤡️️ TikTok scrolling'), ('self-development', '🧑📚️ Self-development'), ('reading', '📚️ Reading'), ('architecture', '🏛️️ Architecture'), ('hiking', '⛰️ Hiking'), ('photo', '📸 Photography'), ('coffee', '☕ Coffee'), ('dance', '💃 Dancing'), ('footbal', '⚽ Football'), ('food', '🍲 Food'), ('IT', '🧑\u200d💻 IT'), ('volleyball', '🏐️ Volleyball'), ('video-making', '🎥 Video-making'), ('fashion', '🧥️ Fashion')], default=None, max_length=24), blank=True, default=list, size=None, verbose_name='issuer interests'),
        ),
    ]

# Generated by Django 4.1 on 2022-08-05 18:41

import apps.utils.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0012_alter_buddyrequest_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequest',
            name='interests',
            field=apps.utils.models.fields.ArrayFieldWithDisplayableChoices(base_field=models.CharField(choices=[('tik-tok', '🤡️️ TikTok scrolling'), ('pets', '🐕️ Pets'), ('movies', '🎞️ Movies'), ('shopping', '🛍️️ Shopping'), ('party', '🎉 Partying'), ('theatre', '🎭️ Theatre'), ('IT', '🧑\u200d💻 IT'), ('yoga', '🧘️ Yoga'), ('photo', '📸 Photography'), ('footbal', '⚽ Football'), ('music', '🎶 Music'), ('running', '🏃\u200d♀️ Running'), ('travel', '✈ Travelling'), ('video-making', '🎥 Video-making'), ('self-development', '🧑📚️ Self-development'), ('food', '🍲 Food'), ('dance', '💃 Dancing'), ('volleyball', '🏐️ Volleyball'), ('coffee', '☕ Coffee'), ('fashion', '🧥️ Fashion'), ('reading', '📚️ Reading'), ('hiking', '⛰️ Hiking'), ('architecture', '🏛️️ Architecture')], default=None, max_length=24), blank=True, default=list, size=None, verbose_name='issuer interests'),
        ),
    ]
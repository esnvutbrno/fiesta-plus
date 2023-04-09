# Generated by Django 4.2 on 2023-04-08 22:15

import apps.utils.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0016_alter_buddyrequest_interests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequest',
            name='interests',
            field=apps.utils.models.fields.ArrayFieldWithDisplayableChoices(base_field=models.CharField(choices=[('knitting', '🧶 Knitting'), ('architecture', '🏛️️ Architecture'), ('metalworking', '🔨 Metalworking'), ('swimming', '🏊 Swimming'), ('cricket', '🏏 Cricket'), ('running', '🏃\u200d♀️ Running'), ('gaming', '🎮 Gaming'), ('woodworking', '🪵 Woodworking'), ('tik-tok', '🤡️️ TikTok scrolling'), ('table_tennis', '🏓 Table Tennis'), ('badminton', '🏸 Badminton'), ('painting', '🎨 Painting'), ('parkour', '🤸 Parkour'), ('dance', '💃 Dancing'), ('acting', '🎭 Acting'), ('diving', '🤿 Diving'), ('graphic design', '🎨 Graphic Design'), ('volleyball', '🏐️ Volleyball'), ('biking', '🚴 Biking'), ('self-development', '🧑📚️ Self-development'), ('coffee', '☕ Coffee'), ('IT', '🧑\u200d💻 IT'), ('theatre', '🎭️ Theatre'), ('pottery', '🏺 Pottery'), ('food', '🍲 Food'), ('reading', '📚️ Reading'), ('fashion', '🧥️ Fashion'), ('baking', '🧁 Baking'), ('yoga', '🧘️ Yoga'), ('tennis', '🎾 Tennis'), ('filmmaking', '🎥 Filmmaking'), ('sculpture', '🗿 Sculpture'), ('writing', '✍️ Writing'), ('travel', '✈ Travelling'), ('hiking', '⛰️ Hiking'), ('shopping', '🛍️️ Shopping'), ('party', '🎉 Partying'), ('movies', '🎞️ Movies'), ('snowboarding', '🏂 Snowboarding'), ('skiing', '⛷️ Skiing'), ('photo', '📸 Photography'), ('animation', '🎬 Animation'), ('music', '🎶 Music'), ('sewing', '🧵 Sewing'), ('crocheting', '🪡 Crocheting'), ('rock_climbing', '🧗 Rock Climbing'), ('video-making', '🎥 Video-making'), ('web_development', '🌐 Web Development'), ('soccer', '⚽ Soccer'), ('drawing', '✏️ Drawing'), ('football', '⚽ Football'), ('singing', '🎤 Singing'), ('podcasting', '🎙️ Podcasting'), ('golf', '⛳ Golf'), ('surfing', '🏄 Surfing'), ('pets', '🐕️ Pets'), ('coding', '💻 Coding'), ('karaoke', '🎤 Karaoke'), ('skateboarding', '🛹 Skateboarding'), ('basketball', '🏀 Basketball'), ('video_editing', '🎞️ Video Editing'), ('cooking', '🍳 Cooking')], default=None, max_length=24), blank=True, default=list, size=None, verbose_name='issuer interests'),
        ),
        migrations.AlterField(
            model_name='buddysystemconfiguration',
            name='matching_policy',
            field=models.CharField(choices=[('manual-by-editor', 'Manual by editors'), ('manual-by-member', 'Manual by members'), ('same-faculty', 'Restricted to same faculty'), ('same-faculty-limited', 'Restricted to same faculty with limit')], default='manual-by-editor', help_text='Manual by editors: Matching is done manually only by editors. <br />Manual by members: Matching is done manually directly by members. <br />Restricted to same faculty: Matching is done manually by members themselves, but limited to the same faculty. <br />Restricted to same faculty with limit: Matching is done manually by members themselves, but limited to same faculty tillthe rolling limit - limitation is not enabled after reaching the limit.', max_length=32),
        ),
    ]
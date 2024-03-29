# Generated by Django 4.0.6 on 2022-07-27 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_system', '0002_buddysystemconfiguration_display_issuer_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='buddyrequest',
            name='description',
            field=models.TextField(default='description', verbose_name='description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='buddysystemconfiguration',
            name='matching_policy',
            field=models.CharField(choices=[('manual-by-editor', 'Manual by editors'), ('manual-by-member', 'Manual by members'), ('same-faculty', 'Limited by faculty'), ('same-faculty-limited', 'Limited by faculty till limit')], default='manual-by-editor', help_text='Manual by editors: Matching done manualy only by editors. <br />Manual by members: Matching is done manualy directly by members. <br />Limited by faculty: Matching done manualy by members themselfs, but limited to the same faculty. <br />Limited by faculty till limit: Matching done manualy by members themselfs, but limited to same faculty tillthe rolling limit - limitation is not enabled after reaching the rolling limit.', max_length=32),
        ),
    ]

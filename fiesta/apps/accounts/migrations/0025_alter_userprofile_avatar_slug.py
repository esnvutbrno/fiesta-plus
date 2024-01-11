# Generated by Django 4.2.7 on 2023-12-17 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_userprofile_avatar_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_slug',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='avatar slug'),
        ),
    ]
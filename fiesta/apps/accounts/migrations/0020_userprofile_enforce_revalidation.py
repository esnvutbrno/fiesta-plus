# Generated by Django 4.2.7 on 2023-11-13 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_remove_userprofile_home_university_or_faculty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='enforce_revalidation',
            field=models.BooleanField(default=False, verbose_name='enforce revalidation of profile'),
        ),
    ]
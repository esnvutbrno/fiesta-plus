# Generated by Django 4.0.2 on 2022-02-21 11:06

from django.db import migrations, models

import apps.utils.models.query


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_userprofile_picture'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='userprofile',
            name='home_university_or_faculty',
        ),
        migrations.AddConstraint(
            model_name='userprofile',
            constraint=models.CheckConstraint(check=apps.utils.models.query.Q(('state', 'incomplete'), apps.utils.models.query.Q(('home_university', None), apps.utils.models.query.Q(('home_faculty', None), _negated=True)), apps.utils.models.query.Q(apps.utils.models.query.Q(('home_university', None), _negated=True), ('home_faculty', None)), _connector='OR'), name='home_university_or_faculty'),
        ),
    ]
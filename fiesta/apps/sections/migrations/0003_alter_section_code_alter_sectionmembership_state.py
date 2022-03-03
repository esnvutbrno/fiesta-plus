# Generated by Django 4.0.2 on 2022-02-18 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0002_alter_sectionmembership_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='code',
            field=models.SlugField(blank=True, help_text='Official code used in ESN world, especially in ESN Accounts database.', null=True, unique=True, verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='sectionmembership',
            name='state',
            field=models.CharField(choices=[('inactive', 'Unconfirmed'), ('active', 'Confirmed'), ('suspended', 'Suspended')], default='inactive', max_length=16, verbose_name='membership state'),
        ),
    ]
# Generated by Django 4.2 on 2023-04-22 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0014_alter_sectionmembership_role'),
        ('esncards', '0005_alter_esncardapplication_holder_photo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='esncardapplication',
            options={'ordering': ('-created', 'state'), 'verbose_name': 'ESNcard application', 'verbose_name_plural': 'ESNcard applications'},
        ),
        migrations.AlterField(
            model_name='esncardapplication',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='esncard_applications', to='sections.section', verbose_name='section'),
        ),
    ]

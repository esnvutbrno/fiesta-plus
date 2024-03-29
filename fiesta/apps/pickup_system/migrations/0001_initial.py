# Generated by Django 4.2.7 on 2023-11-15 23:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import django_lifecycle.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sections', '0021_alter_sectionuniversity_section_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('universities', '0003_alter_faculty_created_alter_faculty_university_and_more'),
        ('plugins', '0017_alter_plugin_app_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('state', models.CharField(choices=[('created', 'Created'), ('matched', 'Matched'), ('cancelled', 'Cancelled')], default='created', max_length=16, verbose_name='state')),
                ('note', models.TextField(verbose_name='text from issuer')),
                ('issuer', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_system_issued_requests', to=settings.AUTH_USER_MODEL, verbose_name='issuer')),
                ('issuer_faculty', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_system_issued_requests', to='universities.faculty', verbose_name="issuer's faculty")),
                ('responsible_section', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_system_requests', to='sections.section', verbose_name='responsible section')),
            ],
            options={
                'verbose_name': 'pickup request',
                'verbose_name_plural': 'pickup requests',
                'ordering': ('-created',),
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PickupSystemConfiguration',
            fields=[
                ('basepluginconfiguration_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='plugins.basepluginconfiguration')),
                ('display_issuer_picture', models.BooleanField(default=False)),
                ('display_issuer_gender', models.BooleanField(default=False)),
                ('display_issuer_country', models.BooleanField(default=False)),
                ('display_issuer_university', models.BooleanField(default=False)),
                ('display_issuer_faculty', models.BooleanField(default=False)),
                ('display_request_creation_date', models.BooleanField(default=True)),
                ('rolling_limit', models.PositiveSmallIntegerField(default=0)),
                ('enable_note_from_matcher', models.BooleanField(default=True, help_text='Allows matcher to reply with custom notes to the request issuer')),
            ],
            options={
                'verbose_name': 'pickup system configuration',
                'verbose_name_plural': 'pickup system configurations',
            },
            bases=('plugins.basepluginconfiguration',),
        ),
        migrations.CreateModel(
            name='PickupRequestMatch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('note', models.TextField(blank=True, verbose_name='text from matcher')),
                ('matcher', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_system_request_matches', to=settings.AUTH_USER_MODEL, verbose_name='matched by')),
                ('matcher_faculty', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_system_request_matches', to='universities.faculty', verbose_name="matcher's faculty")),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='match', to='pickup_system.pickuprequest', verbose_name='request')),
            ],
            options={
                'verbose_name': 'pickup request match',
                'verbose_name_plural': 'pickup request matches',
                'ordering': ('-created',),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]

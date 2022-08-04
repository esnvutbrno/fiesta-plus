from django.db import migrations


def forward(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    db_alias = schema_editor.connection.alias
    s, created = Site.objects.using(db_alias).get_or_create(pk=1)
    s.name = 'Fiesta'
    s.domain = 'fiesta.localhost'
    s.save()


def reverse(apps, schema_editor):
    ...


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="sectionnotificationpreferences",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="sectionnotificationpreferences",
            constraint=models.UniqueConstraint(
                fields=("user", "section"),
                name="unique_user_section_prefs",
            ),
        ),
    ]

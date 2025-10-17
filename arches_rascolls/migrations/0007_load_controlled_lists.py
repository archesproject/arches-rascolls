import io
import os

from django.core import management
from django.db import migrations

from arches_rascolls.settings import APP_ROOT


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0006_add_multicard_descriptor"),
        ("arches_controlled_lists", "0008_ensure_languages_in_sync"),
    ]

    def load_lists(apps, schema_editor):
        management.call_command(
            "loaddata",
            os.path.join(
                APP_ROOT,
                "pkg",
                "reference_data",
                "controlled_lists",
                "rascolls_lists.json",
            ),
            stdout=io.StringIO(),
        )

    operations = [
        migrations.RunPython(load_lists, migrations.RunPython.noop),
    ]

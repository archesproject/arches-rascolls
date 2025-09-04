import io
import os

from django.core import management
from django.db import migrations

from casf_database.settings import APP_ROOT


class Migration(migrations.Migration):

    dependencies = [
        ("casf_database", "0006_add_multicard_descriptor"),
        ("arches_controlled_lists", "0004_reconfigure_listitem_sortorder_constraints"),
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

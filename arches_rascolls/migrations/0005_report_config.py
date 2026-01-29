from django.db import migrations
from django.utils.translation import gettext as _

class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0004_search_layer"),
        (
            "arches_modular_reports",
            "0007_reportconfig_slug",
        ),
    ]

    operations = []

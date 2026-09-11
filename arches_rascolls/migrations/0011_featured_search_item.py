import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0010_plugin_visibility"),
        ("arches_search", "0021_daterangesearch_end_value_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeaturedSearchItem",
            fields=[
                (
                    "featuredsearchitemid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("presentation", models.JSONField(default=dict)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "saved_search",
                    models.ForeignKey(
                        limit_choices_to={"creator__is_staff": True},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="featured_items",
                        to="arches_search.savedsearch",
                    ),
                ),
            ],
            options={
                "db_table": "arches_rascolls_featured_search_items",
                "managed": True,
                "ordering": ["sort_order", "featuredsearchitemid"],
            },
        ),
    ]

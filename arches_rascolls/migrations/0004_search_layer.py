import uuid
from django.db import migrations
from django.utils.translation import gettext as _
import json


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0003_function"),
    ]

    def remove_map_layers(apps, schema_editor):
        MapSource = apps.get_model("models", "MapSource")
        MapLayer = apps.get_model("models", "MapLayer")
        layerids = ("0fd1ef37-f3c8-4e0a-85ce-173068173808",)
        for layerid in layerids:
            try:
                mapbox_layer = MapLayer.objects.get(maplayerid=layerid)
                all_sources = [i.get("source") for i in mapbox_layer.layerdefinitions]
                sources = {i for i in all_sources if i}
                for source in sources:
                    src = MapSource.objects.get(name=source)
                    src.delete()
                mapbox_layer.delete()
            except MapLayer.DoesNotExist:
                continue

    operations = [
        migrations.RunPython(migrations.RunPython.noop, remove_map_layers),
    ]

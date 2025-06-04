import uuid
from django.db import migrations
from django.utils.translation import gettext as _
import json


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0003_function"),
    ]

    def add_map_layers(apps, schema_editor):
        MapSource = apps.get_model("models", "MapSource")
        MapLayer = apps.get_model("models", "MapLayer")

        reference_collection_search = {
            "maplayerid": uuid.UUID("0fd1ef37-f3c8-4e0a-85ce-173068173808"),
            "sortorder": 0,
            "style": {
                "name": "Reference Collection Search",
                "sources": {
                    "rascolls-search": {
                        "type": "vector",
                        "tiles": [
                            "/api-reference-collection-search-mvt/{z}/{x}/{y}.pbf"
                        ],
                        "minzoom": 1,
                    }
                },
                "layers": [
                    {
                        "id": "rascolls-search-point-stroke",
                        "type": "circle",
                        "paint": {
                            "circle-color": "#DE5C1B",
                            "circle-radius": 7,
                            "circle-opacity": 1,
                        },
                        "filter": ["all", ["==", "$type", "Point"]],
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-point",
                        "type": "circle",
                        "paint": {"circle-color": "#FEA811", "circle-radius": 5},
                        "filter": ["all", ["==", "$type", "Point"]],
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-line",
                        "type": "line",
                        "paint": {"line-color": "#DE5C1B", "line-width": 3},
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-polygon-line",
                        "type": "line",
                        "paint": {"line-color": "#DE5C1B", "line-width": 2},
                        "filter": ["==", "$type", "Polygon"],
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-fill",
                        "type": "fill",
                        "paint": {
                            "fill-color": "#FEA811",
                            "fill-opacity": 0.3,
                            "fill-outline-color": "#FEA811",
                        },
                        "filter": ["==", "$type", "Polygon"],
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                ],
            },
            "arches_metadata": {
                "addtomap": True,
                "icon": "fa fa-globe",
                "isoverlay": True,
            },
        }

        layer_configs = (reference_collection_search,)

        for config in layer_configs:
            try:
                config["style"] = json.loads(config["style"])
            except:
                print("Could not parse style")

            layer_name = config["style"]["name"]
            for layer in config["style"]["layers"]:
                if "source" in layer:
                    layer["source"] = layer["source"]
            for source_name, source_dict in config["style"]["sources"].items():
                MapSource.objects.get_or_create(name=source_name, source=source_dict)

            map_layer = MapLayer(
                maplayerid=config["maplayerid"],
                name=layer_name,
                sortorder=config["sortorder"],
                layerdefinitions=config["style"]["layers"],
                **config["arches_metadata"],
            )
            map_layer.save()

    def remove_map_layers(apps, schema_editor):
        MapSource = apps.get_model("models", "MapSource")
        MapLayer = apps.get_model("models", "MapLayer")
        layerids = ("0fd1ef37-f3c8-4e0a-85ce-173068173808",)
        for layerid in layerids:
            mapbox_layer = MapLayer.objects.get(maplayerid=layerid)
            all_sources = [i.get("source") for i in mapbox_layer.layerdefinitions]
            sources = {i for i in all_sources if i}
            for source in sources:
                src = MapSource.objects.get(name=source)
                src.delete()
            mapbox_layer.delete()

    operations = [
        migrations.RunPython(add_map_layers, remove_map_layers),
    ]

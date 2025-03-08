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
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                        "type": "circle",
                        "filter": ["all", ["==", "$type", "Point"]],
                        "paint": {
                            "circle-radius": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                6,
                                4,
                            ],
                            "circle-opacity": 1,
                            "circle-color": "#F05",
                        },
                    },
                    {
                        "id": "rascolls-search-point",
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                        "type": "circle",
                        "filter": ["all", ["==", "$type", "Point"]],
                        "paint": {"circle-radius": 3, "circle-color": "#F05"},
                    },
                    {
                        "id": "rascolls-search-line",
                        "type": "line",
                        "paint": {
                            "line-color": "#F05",
                            "line-width": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                3,
                                1,
                            ],
                        },
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-polygon-line",
                        "type": "line",
                        "paint": {
                            "line-color": "#F05",
                            "line-width": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                3,
                                1,
                            ],
                        },
                        "filter": ["==", "$type", "Polygon"],
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-fill",
                        "type": "fill",
                        "paint": {
                            "fill-color": "#F05",
                            "fill-opacity": 0.5,
                            "fill-outline-color": "#F05",
                        },
                        "filter": ["==", "$type", "Polygon"],
                        "source": "rascolls-search",
                        "source-layer": "rascolls-search",
                    },
                    {
                        "id": "rascolls-search-labels",
                        "type": "symbol",
                        "paint": {
                            "text-color": "#33d",
                            "text-halo-color": "#fff",
                            "text-halo-width": 2.5,
                        },
                        "layout": {
                            "text-font": [
                                "Open Sans Semibold",
                                "Arial Unicode MS Bold",
                            ],
                            "text-size": 18,
                            "text-field": ["get", "quad_name"],
                            "text-justify": "auto",
                            "text-radial-offset": 0.5,
                            "text-variable-anchor": ["top", "bottom", "left", "right"],
                        },
                        "source": "rascolls-search",
                        "minzoom": 9,
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

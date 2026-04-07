import uuid
from django.db import migrations
from django.utils.translation import gettext as _
import json


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ("models", "11499_add_editlog_resourceinstance_idx"),
    ]

    def add_map_layers(apps, schema_editor):
        MapSource = apps.get_model("models", "MapSource")
        MapLayer = apps.get_model("models", "MapLayer")

        reference_collections = {
            "maplayerid": uuid.UUID("0c23d1a3-3e6a-4e72-b413-a2a6c46f828b"),
            "sortorder": 1,
            "style": {
                "name": "Reference Collections",
                "sources": {
                    "referencecollections": {
                        "type": "vector",
                        "tiles": ["/api-reference-collection-mvt/{z}/{x}/{y}.pbf"],
                        "minzoom": 0,
                    }
                },
                "layers": [
                    {
                        "id": "referencecollections-point-stroke",
                        "source": "referencecollections",
                        "source-layer": "referencecollections",
                        "type": "circle",
                        "filter": ["all", ["==", "$type", "Point"]],
                        "paint": {
                            "circle-radius": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                7,
                                6,
                            ],
                            "circle-opacity": 1,
                            "circle-color": "#00f",
                        },
                    },
                    {
                        "id": "referencecollections-point",
                        "source": "referencecollections",
                        "source-layer": "referencecollections",
                        "type": "circle",
                        "filter": ["all", ["==", "$type", "Point"]],
                        "paint": {"circle-radius": 5, "circle-color": "#00A1FF"},
                    },
                    {
                        "id": "referencecollections-line",
                        "type": "line",
                        "paint": {
                            "line-color": "#00f",
                            "line-width": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                3,
                                1,
                            ],
                        },
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "referencecollections",
                        "source-layer": "referencecollections",
                    },
                    {
                        "id": "referencecollections-polygon-line",
                        "type": "line",
                        "paint": {
                            "line-color": "#00f",
                            "line-width": [
                                "case",
                                ["boolean", ["feature-state", "selected"], False],
                                3,
                                1,
                            ],
                        },
                        "filter": ["==", "$type", "Polygon"],
                        "layout": {"line-cap": "round", "line-join": "round"},
                        "source": "referencecollections",
                        "source-layer": "referencecollections",
                    },
                    {
                        "id": "referencecollections-fill",
                        "type": "fill",
                        "paint": {
                            "fill-color": "#00f",
                            "fill-opacity": 0.1,
                            "fill-outline-color": "#00f",
                        },
                        "filter": ["==", "$type", "Polygon"],
                        "source": "referencecollections",
                        "source-layer": "referencecollections",
                    },
                    {
                        "id": "referencecollections-labels",
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
                        "source": "referencecollections",
                        "minzoom": 9,
                        "source-layer": "referencecollections",
                    },
                ],
            },
            "arches_metadata": {
                "addtomap": True,
                "icon": "fa fa-globe",
                "isoverlay": True,
            },
        }

        layer_configs = (reference_collections,)

        for config in layer_configs:
            try:
                config["style"] = json.loads(config["style"])
            except:
                pass
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
        layerids = ("0c23d1a3-3e6a-4e72-b413-a2a6c46f828b",)
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
                pass

    operations = [
        migrations.RunPython(add_map_layers, remove_map_layers),
    ]

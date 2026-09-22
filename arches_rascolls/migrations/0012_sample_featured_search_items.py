from datetime import datetime

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0011_featured_search_item"),
        ("arches_search", "0023_seed_resource_field_facets"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    MATERIAL_NODE_SUBJECT = {
        "type": "NODE",
        "graph_slug": "reference_and_sample_collection_item",
        "node_alias": "material",
        "search_models": [],
    }

    SAVED_SEARCHES = [
        {
            "savedsearchid": "5769e2af-3892-4ec4-855c-00c05d2d81af",
            "name": "glass",
            "materials": ["glass"],
            "created_at": "2026-09-21T14:19:10.680769-07:00",
        },
        {
            "savedsearchid": "4b97adff-a104-4ada-80dc-7ed4dd1fed5d",
            "name": "wood",
            "materials": ["wood"],
            "created_at": "2026-09-21T14:19:37.764329-07:00",
        },
        {
            "savedsearchid": "824e32ef-c34b-4bde-a39e-85e3162304cc",
            "name": "materials_paint",
            "materials": [
                "paint, acrylic",
                "paint, enamel",
                "paint, encaustic",
                "paint, gouache",
                "paint, oil-based",
                "paint, oil-based, water mixable",
                "paint, other",
                "paint, tempera",
                "paint, watercolor",
            ],
            "created_at": "2026-09-21T14:18:44.698906-07:00",
        },
        {
            "savedsearchid": "0b14aca5-9aae-4c81-82bd-e1b644ce7440",
            "name": "watercolor_paint",
            "materials": ["paint, watercolor"],
            "created_at": "2026-09-21T14:26:30.915762-07:00",
        },
        {
            "savedsearchid": "3d4c48f4-fdbf-488c-9229-edd87d585f76",
            "name": "stone",
            "materials": ["stone, artificial", "stone, natural", "stone, unspecified"],
            "created_at": "2026-09-21T15:09:10.438980-07:00",
        },
        {
            "savedsearchid": "b6d80616-44c9-4e03-8833-2f8af56ffef4",
            "name": "artificial_stone",
            "materials": ["stone, artificial"],
            "created_at": "2026-09-21T15:09:50.949425-07:00",
        },
        {
            "savedsearchid": "2300e694-471c-4879-8630-d50816f66bd7",
            "name": "photographic",
            "materials": ["photographic film", "photographic paper"],
            "created_at": "2026-09-21T15:10:54.512396-07:00",
        },
    ]

    FEATURED_SEARCH_ITEMS = [
        {
            "featuredsearchitemid": "a4075820-e0ee-431d-8f1c-da09fb59a573",
            "saved_search_id": "5769e2af-3892-4ec4-855c-00c05d2d81af",
            "presentation": {
                "icon": "pi-sparkles",
                "color": "#7FFFD4",
                "label": "Glass",
                "description": (
                    "Material fragments extracted from larger glass artworks, "
                    "representing specific colored panes, fused sections, or blown "
                    "glass components used in the overall piece"
                ),
            },
            "sort_order": 0,
            "is_active": True,
            "created_at": "2026-09-21T14:23:15.597352-07:00",
        },
        {
            "featuredsearchitemid": "ad76f8e6-8791-4bff-9806-ebd8c6cb5da7",
            "saved_search_id": "4b97adff-a104-4ada-80dc-7ed4dd1fed5d",
            "presentation": {
                "icon": "pi-box",
                "color": "#8B4513",
                "label": "Wood",
                "description": (
                    "Representative cuts or swatches taken from a larger wooden "
                    "artwork, showcasing specific wood species, carved details, "
                    "joinery, or surface treatments"
                ),
            },
            "sort_order": 1,
            "is_active": True,
            "created_at": "2026-09-21T14:23:34.981056-07:00",
        },
        {
            "featuredsearchitemid": "ff097227-aa14-4c88-a3fa-2108e253df4d",
            "saved_search_id": "824e32ef-c34b-4bde-a39e-85e3162304cc",
            "presentation": {
                "icon": "pi-palette",
                "color": "#FF5733",
                "label": "Paint",
                "description": (
                    "Paint chips, layer cross-sections, or swatch tests taken from "
                    "a larger painting, capturing specific color mixtures, "
                    "application textures, or protective finishes"
                ),
            },
            "sort_order": 2,
            "is_active": True,
            "created_at": "2026-09-21T14:21:55.907463-07:00",
        },
        {
            "featuredsearchitemid": "4869e205-1df1-4938-8e16-a5c5698120f2",
            "saved_search_id": "0b14aca5-9aae-4c81-82bd-e1b644ce7440",
            "presentation": {
                "icon": "pi-pencil",
                "color": "#4682B4",
                "label": "Watercolor Paint",
                "description": (
                    "Samples taken from a larger watercolor piece, illustrating "
                    "specific wash techniques, color blends, or paper-pigment "
                    "interactions"
                ),
            },
            "sort_order": 3,
            "is_active": True,
            "created_at": "2026-09-21T14:28:13.374354-07:00",
        },
        {
            "featuredsearchitemid": "ed555402-0947-4120-b2a5-58fe86ec5d71",
            "saved_search_id": "2300e694-471c-4879-8630-d50816f66bd7",
            "presentation": {
                "icon": "pi-camera",
                "color": "#2F4F4F",
                "label": "Photographic Film/Paper",
                "description": (
                    "Film strip segments or paper print swatches sourced from a "
                    "larger photographic work, highlighting emulsion properties, "
                    "tonality, or exposure characteristics"
                ),
            },
            "sort_order": 4,
            "is_active": True,
            "created_at": "2026-09-21T15:11:59.354377-07:00",
        },
        {
            "featuredsearchitemid": "cc05ed7d-8509-411b-a80f-2f3b6759a90a",
            "saved_search_id": "3d4c48f4-fdbf-488c-9229-edd87d585f76",
            "presentation": {
                "icon": "pi-table",
                "color": "#A9A9A9",
                "label": "Stone",
                "description": (
                    "Raw or finished rock chips taken from a larger stone "
                    "sculpture or installation, displaying specific geological "
                    "veining, natural coloration, and surface tooling"
                ),
            },
            "sort_order": 5,
            "is_active": True,
            "created_at": "2026-09-21T15:12:47.652019-07:00",
        },
        {
            "featuredsearchitemid": "9dbbee51-a52b-470e-a3ac-29f475465ec0",
            "saved_search_id": "b6d80616-44c9-4e03-8833-2f8af56ffef4",
            "presentation": {
                "icon": "pi-truck",
                "color": "#D3D3D3",
                "label": "Artificial Stone",
                "description": (
                    "Composite or cast material samples taken from a larger "
                    "engineered stone artwork, demonstrating the synthetic "
                    "matrix, aggregate blend, and uniform surface finish."
                ),
            },
            "sort_order": 6,
            "is_active": True,
            "created_at": "2026-09-21T15:15:31.640647-07:00",
        },
    ]

    def material_query(*values):
        return {
            "terms": [],
            "queries": {
                "material": {
                    "logic": "AND",
                    "scope": "RESOURCE",
                    "groups": [],
                    "clauses": [
                        {
                            "type": "LITERAL",
                            "subject": Migration.MATERIAL_NODE_SUBJECT,
                            "operands": [{"type": "LITERAL", "value": list(values)}],
                            "operator": "REFERENCES_ANY",
                            "quantifier": "ANY",
                        }
                    ],
                    "graph_slug": "reference_and_sample_collection_item",
                    "aggregations": [],
                    "relationship": None,
                }
            },
            "mapFilter": None,
            "graphSlugs": ["reference_and_sample_collection_item"],
        }

    def add_featured_search_items(apps, schema_editor):
        User = apps.get_model(settings.AUTH_USER_MODEL)
        SavedSearch = apps.get_model("arches_search", "SavedSearch")
        FeaturedSearchItem = apps.get_model("arches_rascolls", "FeaturedSearchItem")

        creator = User.objects.get(pk=1)

        for entry in Migration.SAVED_SEARCHES:
            saved_search, _ = SavedSearch.objects.update_or_create(
                savedsearchid=entry["savedsearchid"],
                defaults={
                    "name": entry["name"],
                    "description": "",
                    "query_definition": Migration.material_query(*entry["materials"]),
                    "creator": creator,
                },
            )
            SavedSearch.objects.filter(pk=saved_search.pk).update(
                created_at=datetime.fromisoformat(entry["created_at"])
            )

        for entry in Migration.FEATURED_SEARCH_ITEMS:
            item, _ = FeaturedSearchItem.objects.update_or_create(
                featuredsearchitemid=entry["featuredsearchitemid"],
                defaults={
                    "saved_search_id": entry["saved_search_id"],
                    "presentation": entry["presentation"],
                    "sort_order": entry["sort_order"],
                    "is_active": entry["is_active"],
                },
            )
            FeaturedSearchItem.objects.filter(pk=item.pk).update(
                created_at=datetime.fromisoformat(entry["created_at"])
            )

    def remove_featured_search_items(apps, schema_editor):
        SavedSearch = apps.get_model("arches_search", "SavedSearch")
        FeaturedSearchItem = apps.get_model("arches_rascolls", "FeaturedSearchItem")

        FeaturedSearchItem.objects.filter(
            featuredsearchitemid__in=[
                entry["featuredsearchitemid"]
                for entry in Migration.FEATURED_SEARCH_ITEMS
            ]
        ).delete()
        SavedSearch.objects.filter(
            savedsearchid__in=[
                entry["savedsearchid"] for entry in Migration.SAVED_SEARCHES
            ]
        ).delete()

    operations = [
        migrations.RunPython(
            add_featured_search_items,
            remove_featured_search_items,
        ),
    ]

import json
from http import HTTPStatus

from django.core.cache import caches
from django.utils.translation import gettext as _
from django.views.generic import View
from django.http import HttpResponse
from django.db import connection

from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.file_validator import FileValidator
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.permission_backend import user_can_read_map_layers
from afrc.utils.geo_utils import GeoUtils
from django.http import Http404

searchresults_cache = caches["searchresults"]


class MapDataAPI(View):
    def get(self, request):
        map_layers = user_can_read_map_layers(request.user)
        map_sources = list(models.MapSource.objects.all())
        for map_source in map_sources:
            if "tiles" in map_source.source:
                if not map_source.source["tiles"][0].startswith("http"):
                    source = "{}{}".format(
                        settings.PUBLIC_SERVER_ADDRESS, map_source.source["tiles"][0]
                    )
                    map_source.source["tiles"][0] = source

        return JSONResponse(
            {
                "map_layers": map_layers,
                "map_sources": map_sources,
                # "resource_map_layers": resource_map_layers,
                # "resource_map_sources": resource_map_sources,
            }
        )


class FeatureGeometriesAPI(View):
    def get(self, request):
        resource_instance_id = request.GET.get("resource_instance_id")

        se = SearchEngineFactory().create()
        document = se.search(index=RESOURCES_INDEX, id=resource_instance_id)

        geo_utils = GeoUtils()

        for geometry in document["_source"]["geometries"]:
            geometry["centroid"] = geo_utils.get_centroid(geometry["geom"])

        return JSONResponse(document["_source"]["geometries"])


class ResourceInstancesWithinGeometryAndBufferAPI(View):
    def post(self, request):
        data = json.loads(request.body)

        geo_utils = GeoUtils()

        intersection_and_difference_of_feature_collections = (
            geo_utils.get_intersection_and_difference_of_feature_collections(
                data["drawnFeatures"], data["bufferedFeatures"]
            )
        )

        return JSONResponse(
            {
                "resources_intersecting_drawn_features": geo_utils.get_resource_instances_within_feature_collection(
                    data["drawnFeatures"]
                ),
                "resources_intersecting_buffered_features": geo_utils.get_resource_instances_within_feature_collection(
                    data["bufferedFeatures"]
                ),
                "resources_intersecting_buffers": geo_utils.get_resource_instances_within_feature_collection(
                    {
                        "type": "FeatureCollection",
                        "features": [
                            feature
                            for feature in intersection_and_difference_of_feature_collections[
                                "features"
                            ]
                            if feature["properties"].get("feature_type")
                            == "difference_from_second"
                        ],
                    }
                ),
            }
        )


class FeatureBufferAPI(View):
    def post(self, request):
        data = json.loads(request.body)
        features = data["features"]
        geo_utils = GeoUtils()
        buffered = geo_utils.buffer_feature_collection(features)
        return JSONResponse(buffered)


class GeoJSONBoundsAPI(View):
    def post(self, request):
        geo_utils = GeoUtils()

        return JSONResponse(geo_utils.get_bounds_from_geojson(json.loads(request.body)))


class GeoJSONParseIntoCollectionAPI(View):
    """Reshape arbitrary GeoJSON into a feature collection. The reshaping could
    be done without a trip to the server, but doing so allows us to enforce
    consistent (project-wide) file validation rules.
    """

    def post(self, request):
        feature_file = request.FILES.get("geojson")
        if not feature_file:
            return JSONErrorResponse(
                message=_("A geojson file is required."),
                status=HTTPStatus.BAD_REQUEST,
            )

        validator = FileValidator()
        if file_type_errors := validator.validate_file_type(feature_file):
            return JSONErrorResponse(
                message="\n".join(file_type_errors),
                status=HTTPStatus.BAD_REQUEST,
            )

        feature_file.seek(0)
        geojson_obj = json.load(feature_file)

        return JSONResponse(GeoUtils.shape_geojson_as_feature_collection(geojson_obj))


class ReferenceCollectionSearchMVT(View):
    def get(self, request, zoom, x, y):
        system_settings_resourceid = settings.SYSTEM_SETTINGS_RESOURCE_ID
        result = None
        with connection.cursor() as cursor:
            session_id = request.session.session_key
            resource_ids = searchresults_cache.get(session_id, [])
            if resource_ids:
                result = cursor.execute(
                    """
                    SELECT ST_AsMVT(tile, 'rascolls-search', 4096, 'geom', 'id')
                    FROM (
                    SELECT
                        id,
                        resourceinstanceid,
                        nodeid,
                        ST_AsMVTGeom(
                            geom,
                            TileBBox(%s, %s, %s, 3857),
                            4096,
                            256,
                            false
                        ) geom
                    FROM geojson_geometries gg
                    WHERE nodeid='bda54e4a-d376-11ef-a239-0275dc2ded29' and resourceinstanceid != %s and resourceinstanceid in %s and (gg.geom && ST_TileEnvelope(%s, %s, %s, margin => (64.0 / 4096)))
                    ) tile
                    """,
                    [
                        zoom,
                        x,
                        y,
                        system_settings_resourceid,
                        tuple(resource_ids),
                        zoom,
                        x,
                        y,
                    ],
                )
                result = bytes(cursor.fetchone()[0]) if result is None else result
            else:
                raise Http404("No search results found")
        return HttpResponse(result, content_type="application/x-protobuf")


class ReferenceCollectionMVT(View):
    def get(self, request, zoom, x, y):
        system_settings_resourceid = settings.SYSTEM_SETTINGS_RESOURCE_ID
        result = None
        with connection.cursor() as cursor:
            result = cursor.execute(
                """
                SELECT ST_AsMVT(tile, 'referencecollections', 4096, 'geom', 'id')
                FROM (
                SELECT
                    id,
                    resourceinstanceid,
                    nodeid,
                    ST_AsMVTGeom(
                        geom,
                        TileBBox(%s, %s, %s, 3857),
                        4096,
                        256,
                        false
                    ) geom
                FROM geojson_geometries gg
                WHERE nodeid='bda54e4a-d376-11ef-a239-0275dc2ded29' and resourceinstanceid != %s and (gg.geom && ST_TileEnvelope(%s, %s, %s, margin => (64.0 / 4096)))
                ) tile
                """,
                [
                    zoom,
                    x,
                    y,
                    system_settings_resourceid,
                    zoom,
                    x,
                    y,
                ],
            )
            result = bytes(cursor.fetchone()[0]) if result is None else result

        return HttpResponse(result, content_type="application/x-protobuf")

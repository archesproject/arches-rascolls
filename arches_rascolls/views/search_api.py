"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import math

from django.core.cache import caches
from django.core.paginator import Paginator
from django.views.generic import View
from django.db import connection
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import Transform, Centroid
from django.contrib.gis.geos import GEOSGeometry
from django.utils.translation import get_language, gettext as _
from django.db.models import Q
from django.db.models.fields.json import KT

from arches.app.models.models import GeoJSONGeometry, ResourceInstance, TileModel
from arches.app.utils.response import JSONResponse
from arches.app.models.system_settings import settings

from arches_rascolls.utils.geo_utils import GeoUtils

logger = logging.getLogger(__name__)

searchresults_cache = caches["searchresults"]


class SearchAPI(View):
    def get(self, request):
        current_page = int(request.GET.get("paging-filter", 1))
        page_size = int(settings.SEARCH_ITEMS_PER_PAGE)
        results = []

        if term_filter := request.GET.get("term-filter", None):
            terms = json.loads(term_filter)
            if terms:
                terms = [term["text"] for term in terms]
            results = get_related_resources_by_text(terms, settings.COLLECTIONS_GRAPHID)
        else:
            results = ResourceInstance.objects.filter(
                graph_id=settings.COLLECTIONS_GRAPHID
            ).values_list("resourceinstanceid")

        if map_filter := json.loads(request.GET.get("map-filter", "[]")):
            geo_utils = GeoUtils()
            spatial_filters = Q()
            for feature in map_filter:
                raw_geom = GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)
                for geom in geo_utils.split_polygon_at_antimeridian(raw_geom):
                    if geom.geom_type == "Point":
                        spatial_filters |= Q(geom__intersects=geom.buffer(0.000001))
                    else:
                        spatial_filters |= Q(geom__intersects=geom)

            resourceids_in_buffer = GeoJSONGeometry.objects.filter(
                spatial_filters, Q(node_id="bda54e4a-d376-11ef-a239-0275dc2ded29")
            ).values_list("resourceinstance_id")

            results = set(resourceids_in_buffer).intersection(set(results))

        if advanced_search_filter := request.GET.get("advanced-search", None):
            advanced_search_results = []
            advanced_search_filter = json.loads(advanced_search_filter)
            query = Q()
            # [{'op': 'and', 'e9b8d73c-09b7-11f0-b84f-0275dc2ded29': {'op': 'eq', 'val': 'f697d7f2-4956-4b14-8910-c7ca673e74ca'}}]
            for filter in advanced_search_filter:
                if filter["op"] == "and":
                    for key, value in filter.items():
                        if key != "op":
                            query &= Q(**{f"data__{key}": value["val"]})
                elif filter["op"] == "or":
                    for key, value in filter.items():
                        if key != "op":
                            query |= Q(**{f"data__{key}": value["val"]})
                elif filter["op"] == "not":
                    # Handle "not" operation
                    pass
                else:
                    # Handle other operations
                    pass

            advanced_search_results = TileModel.objects.filter(query).values_list(
                "resourceinstance_id"
            )
            results = set(advanced_search_results).intersection(set(results))

        session_id = request.session._get_or_create_session_key()

        if term_filter or map_filter or advanced_search_filter:
            searchresults_cache.set(session_id, [str(id[0]) for id in results])
        else:
            searchresults_cache.clear()

        ret = get_search_results_by_resourceids(
            [str(row[0]) for row in results],
            start=(current_page - 1) * page_size,
            limit=page_size,
        )
        return JSONResponse(
            {"results": ret, "total_results": len(results), "page_size": page_size}
        )


def get_current_location(resource):
    try:
        place = (
            resource.from_resxres.filter(node_id="bda4a954-d376-11ef-a239-0275dc2ded29")
            .first()
            .to_resource.name
        )
    except AttributeError:
        place = None

    try:
        TileModel.objects.filter(resourceinstance_id=resource.pk)
        statement_value = (
            TileModel.objects.filter(
                resourceinstance_id=resource.pk,
                nodegroup_id="c7ab9e8a-08e1-11f0-a3e8-0275dc2ded29",
            )
            .annotate(
                location_description=KT(
                    f'data__{"c7abb924-08e1-11f0-a3e8-0275dc2ded29"}'
                )
            )
            .values_list("location_description", flat=True)
            .first()
        )
        statement = json.loads(statement_value)["en"]["value"]
    except TypeError:
        statement = None

    return " | ".join([str(value) for value in [place, statement] if value is not None])


def get_related_resources_by_text(search_query, graphid):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT * FROM __arches_rascolls_get_related_resources_by_searchable_values(%s, %s)",
            [search_query, graphid],
        )
        rows = cursor.fetchall()
    return rows


def get_search_results_by_resourceids(
    resourceids, start=0, limit=settings.SEARCH_ITEMS_PER_PAGE
):
    resource_paginator = Paginator(resourceids, limit)
    page = math.ceil((start + 1) / limit)
    resources = ResourceInstance.objects.filter(
        pk__in=resource_paginator.page(page).object_list
    ).prefetch_related("geojsongeometry_set")
    results = []
    lang = get_language()
    for resource_instance in resources:
        res = {"currentlocation": get_current_location(resource_instance)}
        res["resourceinstanceid"] = resource_instance.resourceinstanceid
        res["displayname"] = resource_instance.descriptors[lang]["name"]
        res["displaydescription"] = resource_instance.descriptors[lang]["description"]
        res["displayname_language"] = lang
        res["has_geom"] = resource_instance.geojsongeometry_set.exists()
        if res["has_geom"]:
            res["centroid"] = (
                resource_instance.geojsongeometry_set.all()
                .annotate(centroid=Centroid(Union("geom")))
                .annotate(wgs=Transform("geom", 4326))
                .first()
                .wgs.coords
            )
        results.append(res)
    return results

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

import logging
import json

from django.views.generic import View
from django.db import connection
from django.utils.translation import get_language, gettext as _
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry

from arches.app.models.models import GeoJSONGeometry, ResourceInstance
from arches.app.models.system_settings import settings
from arches.app.search.components.search_results import get_localized_descriptor
from arches.app.search.elasticsearch_dsl_builder import Query, Ids
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)


class SearchAPI(View):
    def get(self, request):
        current_page = int(request.GET.get("paging-filter", 1))
        page_size = int(settings.SEARCH_ITEMS_PER_PAGE)

        if "term-filter" in request.GET:
            terms = json.loads(request.GET.get("term-filter", None))
            if terms:
                terms = [term["value"] for term in terms]
            results = get_related_resources_by_text(terms, settings.COLLECTIONS_GRAPHID)
        else:
            results = ResourceInstance.objects.filter(
                graph_id=settings.COLLECTIONS_GRAPHID
            ).values_list("resourceinstanceid")

        if map_filter := json.loads(request.GET.get("map-filter", "[]")):
            spatial_filters = Q()
            for feature in map_filter:
                geom = GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)
                spatial_filters |= Q(geom__intersects=geom)

            resourceids_in_buffer = GeoJSONGeometry.objects.filter(
                spatial_filters
            ).values_list("resourceinstance_id")

            results = set(resourceids_in_buffer).intersection(set(results))

        # print(f"len of results: {len(results)}")
        ret = get_search_results_by_resourceids(
            [str(row[0]) for row in results],
            start=(current_page - 1) * page_size,
            limit=page_size,
        )
        return JSONResponse(
            {"results": ret, "total_results": len(results), "page_size": page_size}
        )


def get_related_resources_by_text(search_query, graphid):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT * FROM __afrc_get_related_resources_by_searchable_values(%s, %s)",
            [search_query, graphid],
        )
        rows = cursor.fetchall()
    return rows


def get_search_results_by_resourceids(
    resourceids, start=0, limit=settings.SEARCH_ITEMS_PER_PAGE
):
    se = SearchEngineFactory().create()
    query = Query(se, start=start, limit=limit)
    query.add_query(Ids(ids=resourceids))
    results = query.search(index=RESOURCES_INDEX)

    descriptor_types = ("displaydescription", "displayname")
    active_and_default_language_codes = (get_language(), settings.LANGUAGE_CODE)
    for result in results["hits"]["hits"]:
        for descriptor_type in descriptor_types:
            descriptor = get_localized_descriptor(
                result, descriptor_type, active_and_default_language_codes
            )
            if descriptor:
                result["_source"][descriptor_type] = descriptor["value"]
                if descriptor_type == "displayname":
                    result["_source"]["displayname_language"] = descriptor["language"]
            else:
                result["_source"][descriptor_type] = _("Undefined")
    return results

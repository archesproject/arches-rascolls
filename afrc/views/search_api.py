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

from arches.app.models.models import ResourceXResource, ResourceInstance
from arches.app.models.system_settings import settings
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.components.search_results import get_localized_descriptor
from arches.app.search.elasticsearch_dsl_builder import Query, Ids, Bool, Match, Nested
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.response import JSONResponse, JSONErrorResponse

from arches.app.search.es_mapping_modifier import EsMappingModifier


logger = logging.getLogger(__name__)


# Need to use this rather then the search_results function in arches.app.vies.search
# because we need to return the results rather than the response object
def search_results(request, returnDsl=False):
    search_filter_factory = SearchFilterFactory(request)
    searchview_component_instance = search_filter_factory.get_searchview_instance()

    if not searchview_component_instance:
        unavailable_searchview_name = search_filter_factory.get_searchview_name()
        message = _("No search-view named {0}").format(unavailable_searchview_name)
        return JSONErrorResponse(
            _("Search Failed"),
            message,
            status=400,
        )

    try:
        response_object, search_query_object = (
            searchview_component_instance.handle_search_results_query(
                search_filter_factory, returnDsl
            )
        )
        if returnDsl:
            return search_query_object.pop("query")
        else:
            return response_object
    except Exception as e:
        message = _("There was an error retrieving the search results")
        try:
            message = e.args[0].get("message", message)
        except:
            logger.exception("Error retrieving search results:")
            logger.exception(e)

        return JSONErrorResponse(
            _("Search Failed"),
            message,
            status=500,
        )


class SearchAPI(View):
    def get(self, request):
        base_resource_type_filter = [
            {
                "graphid": settings.COLLECTIONS_GRAPHID,
                "inverted": False,
            }
        ]

        current_page = int(request.GET.get("paging-filter", 1))
        page_size = int(settings.SEARCH_ITEMS_PER_PAGE)
        print(page_size)

        if "term-filter" in request.GET:
            terms = json.loads(request.GET.get("term-filter", None))
            if terms:
                terms = [term["value"] for term in terms]
            results = get_related_resources_by_text(terms)
            print(f"len of results: {len(results)}")
            ret = get_search_results_by_resourceids(
                [str(row[0]) for row in results],
                start=(current_page - 1) * page_size,
                limit=page_size,
            )
            return JSONResponse({"results": ret, "total_results": len(results)})
        else:
            request_copy = request.GET.copy()
            request_copy["resource-type-filter"] = json.dumps(base_resource_type_filter)
            request.GET = request_copy
            direct_results = search_results(request)
            print(current_page * page_size)
            # print(direct_results)
            print(direct_results["total_results"])

            return JSONResponse(content=search_results(request))


def get_related_resources_by_text(search_query):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT * FROM __afrc_get_related_resources_by_searchable_values(%s, '1810d182-b4b5-11ea-84f7-3af9d3b32b71')",
            [search_query],
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

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

from arches.app.models.models import ResourceXResource
from arches.app.models.system_settings import settings
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.components.search_results import get_localized_descriptor
from arches.app.search.elasticsearch_dsl_builder import Query, Ids
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.response import JSONResponse, JSONErrorResponse

logger = logging.getLogger(__name__)


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

        current_page = request.GET.get("paging-filter", 1)
        page_size = int(settings.SEARCH_ITEMS_PER_PAGE)
        print(page_size)

        request_copy = request.GET.copy()
        request_copy["resource-type-filter"] = json.dumps(base_resource_type_filter)
        request.GET = request_copy
        direct_results = search_results(request)
        print(current_page * page_size)
        print(direct_results["total_results"])

        if direct_results["total_results"] >= current_page * page_size:
            print("we have direct hits on collections")
            return JSONResponse(content=search_results(request))
        else:
            # we have no more direct hits on reference collections and we need to
            # backfill with results of hits based on potential resources related to reference collections
            # So first we need to search for resources that aren't reference collections and that match our search criteria
            # then we take those resource instance ids and do a recursive search for any of those
            # resources that might be related to reference collections
            # and return a list of those reference collections
            base_resource_type_filter[0]["inverted"] = True

            request_copy = request.GET.copy()
            request_copy["resource-type-filter"] = json.dumps(base_resource_type_filter)
            request_copy["paging-filter"] = 1
            request.GET = request_copy
            backfill_results = search_results(request)

            # first page of hits of potentially related resources
            resourceinstanceids = [
                hit["_source"]["resourceinstanceid"]
                for hit in backfill_results["results"]["hits"]["hits"]
            ]

            related_resource_ids = list(
                search_relationships_via_ORM(
                    resourceinstanceids,
                    target_graphid=settings.COLLECTIONS_GRAPHID,
                    depth=3,
                )
            )

            se = SearchEngineFactory().create()
            query = Query(se, start=0, limit=30)
            query.add_query(Ids(ids=related_resource_ids))
            results = query.search(index=RESOURCES_INDEX)

            descriptor_types = ("displaydescription", "displayname")
            active_and_default_language_codes = (get_language(), settings.LANGUAGE_CODE)
            for result in results["hits"]["hits"]:
                for descriptor_type in descriptor_types:
                    descriptor = get_localized_descriptor(
                        result, descriptor_type, active_and_default_language_codes
                    )
                    if descriptor:
                        print(descriptor)
                        result["_source"][descriptor_type] = descriptor["value"]
                        if descriptor_type == "displayname":
                            result["_source"]["displayname_language"] = descriptor[
                                "language"
                            ]
                    else:
                        result["_source"][descriptor_type] = _("Undefined")
            direct_results["results"]["hits"]["hits"] += results["hits"]["hits"]
            direct_results["total_results"] += int(len(results["hits"]["hits"]))
            return JSONResponse(direct_results)


def search_relationships_via_ORM(
    resourceinstanceids=None,
    target_graphid=None,
    depth=1,
):
    hits = set()

    # This is a placeholder for the ORM version of the search_relationships function
    # This function should return a list of resourceinstanceids of reference collections
    # that are related to the given list of resourceinstanceids
    def get_related_resourceinstanceids(resourceinstanceids, depth=1):
        depth -= 1
        to_crawl = set()

        # This is a placeholder for the ORM version of the get_related_resourceinstanceids function
        # This function should return a list of resourceinstanceids of resources that are related to
        # the given list of resourceinstanceids
        instances_query = Q(resourceinstanceidfrom__in=resourceinstanceids) | Q(
            resourceinstanceidto__in=resourceinstanceids
        )

        for res in ResourceXResource.objects.filter(instances_query).values_list(
            "resourceinstanceidfrom",
            "resourceinstancefrom_graphid",
            "resourceinstanceidto",
            "resourceinstanceto_graphid",
        ):
            if str(res[1]) != target_graphid:
                to_crawl.add(res[0])
            else:
                hits.add(res[0])

            if str(res[3]) != target_graphid:
                to_crawl.add(res[2])
            else:
                hits.add(res[2])

        if depth > 0:
            get_related_resourceinstanceids(list(to_crawl), depth=depth)

        return hits

    return get_related_resourceinstanceids(resourceinstanceids, depth=depth)


def search_relationships(resourceinstanceids=None, target_graphid=None):
    with connection.cursor() as cursor:
        sql = """
            WITH RECURSIVE resource_traversal_from(resourcexid, resourceid, graphid, depth) AS (
                -- Anchor member: start with the given list of starting resource IDs
                SELECT 
                    resource_x_resource.resourcexid, resourceinstanceidto AS resourceid, resourceinstanceto_graphid AS graphid, 0 AS depth
                FROM 
                    resource_x_resource
                WHERE 
                    resourceinstanceidfrom = ANY(%s::uuid[])

                UNION ALL

                -- Recursive member: traverse the table bidirectionally
                SELECT 
                    resource_x_resource.resourcexid, resource_x_resource.resourceinstanceidto AS resourceid, resourceinstanceto_graphid AS graphid, rt.depth + 1
                FROM 
                    resource_x_resource
                INNER JOIN 
                    resource_traversal_from rt
                ON 
                    resource_x_resource.resourceinstanceidfrom = rt.resourceid
                WHERE 
                    rt.graphid != %s::uuid
                
            ) CYCLE resourcexid SET is_cycle USING path

            SELECT DISTINCT resourceid
            FROM resource_traversal_from
            WHERE graphid = %s::uuid
            AND DEPTH < 3

            UNION (
                WITH RECURSIVE resource_traversal_to(resourcexid, resourceid, graphid, depth) AS (
                    -- Anchor member: start with the given list of starting resource IDs
                    SELECT 
                        resource_x_resource.resourcexid, resourceinstanceidfrom AS resourceid, resourceinstancefrom_graphid AS graphid, 0 AS depth
                    FROM 
                        resource_x_resource
                    WHERE 
                        resourceinstanceidto = ANY(%s::uuid[])
                    
                    UNION ALL
                
                    SELECT 
                        resource_x_resource.resourcexid, resource_x_resource.resourceinstanceidfrom AS resourceid, resourceinstancefrom_graphid AS graphid, rt.depth + 1
                    FROM 
                        resource_x_resource
                    INNER JOIN 
                        resource_traversal_to rt
                    ON 
                        resource_x_resource.resourceinstanceidto = rt.resourceid
                    WHERE 
                        rt.graphid != %s::uuid
                
                ) CYCLE resourcexid SET is_cycle USING path

                SELECT DISTINCT resourceid
                FROM resource_traversal_to
                WHERE graphid = %s::uuid
                AND DEPTH < 3
            )
        """
        print(
            sql
            % (
                resourceinstanceids,
                target_graphid,
                target_graphid,
                resourceinstanceids,
                target_graphid,
                target_graphid,
            )
        )
        cursor.execute(
            sql,
            [
                resourceinstanceids,
                target_graphid,
                target_graphid,
                resourceinstanceids,
                target_graphid,
                target_graphid,
            ],
        )
        hits = []
        # hits = [str(row[0]) for row in cursor.fetchall()]
        for row in cursor.fetchall():
            hits.append(str(row[0]))
        print(len(hits))
        return hits


# {"query": {"ids": {"values": ["fba9bdb3-29a6-3cc2-bd7e-2d3fa7a08c78"]}}, "start": 0, "limit": 0}

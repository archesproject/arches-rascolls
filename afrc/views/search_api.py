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

        # import ipdb

        # ipdb.sset_trace()

        current_page = int(request.GET.get("paging-filter", 1))
        page_size = int(settings.SEARCH_ITEMS_PER_PAGE)
        print(page_size)

        request_copy = request.GET.copy()
        request_copy["resource-type-filter"] = json.dumps(base_resource_type_filter)
        request.GET = request_copy
        direct_results = search_results(request)
        print(current_page * page_size)
        # print(direct_results)
        print(direct_results["total_results"])

        if int(direct_results["total_results"]) >= current_page * page_size:
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
                    depth=2,
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


def search_direct_relationships_via_ORM(
    resourceinstanceids=None,
    depth=1,
):
    hits = set()

    # This is a placeholder for the ORM version of the search_relationships function
    # This function should return a list of resourceinstanceids of reference collections
    # that are related to the given list of resourceinstanceids
    def get_related_resourceinstanceids(resourceinstanceids, depth=1):
        depth -= 1

        # This is a placeholder for the ORM version of the get_related_resourceinstanceids function
        # This function should return a list of resourceinstanceids of resources that are related to
        # the given list of resourceinstanceids
        instances_query = Q(resourceinstanceidfrom__in=resourceinstanceids) | Q(
            resourceinstanceidto__in=resourceinstanceids
        )

        for res in ResourceXResource.objects.filter(instances_query).values_list(
            "resourceinstanceidfrom",
            "resourceinstanceidto",
        ):
            if res[0] not in resourceinstanceids and res[0] not in hits:
                hits.add(res[0])

            if res[2] not in resourceinstanceids and res[2] not in hits:
                hits.add(res[2])

        if depth > 0:
            get_related_resourceinstanceids(list(hits), depth=depth)

        return hits

    return get_related_resourceinstanceids(resourceinstanceids, depth=depth)


class RREsMappingModifier(EsMappingModifier):

    counter = 1

    def __init__(self):
        pass

    @staticmethod
    def get_data_from_function(resourceinstanceids):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM __arches_get_values_for_resourceinstances(%s)",
                [resourceinstanceids],
            )
            rows = cursor.fetchall()
        return rows

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        if str(resourceinstance.graph_id) != settings.COLLECTIONS_GRAPHID:
            return

        if RREsMappingModifier.get_mapping_property() not in document:
            document[RREsMappingModifier.get_mapping_property()] = []

        related_resource_ids = list(
            search_direct_relationships_via_ORM(
                resourceinstanceids=[resourceinstance.resourceinstanceid],
                depth=2,
            )
        )
        # print(related_resource_ids)

        # Example usage
        for item in RREsMappingModifier.get_data_from_function(related_resource_ids):
            # print(item)
            document[RREsMappingModifier.get_mapping_property()].append(item[0])

    @staticmethod
    def create_nested_custom_filter(term, original_element):
        if "nested" not in original_element:
            return original_element
        document_key = RREsMappingModifier.get_mapping_property()
        custom_filter = Bool()
        # custom_filter.should(
        #     Match(
        #         field="%s.custom_value" % document_key,
        #         query=term["value"],
        #         type="phrase_prefix",
        #     )
        # )
        custom_filter.should(
            Match(
                field=document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        nested_custom_filter = Nested(path=document_key, query=custom_filter)
        new_must_element = Bool()
        new_must_element.should(original_element)
        new_must_element.should(nested_custom_filter)
        new_must_element.dsl["bool"]["minimum_should_match"] = 1
        return new_must_element

    @staticmethod
    def add_search_filter(search_query, term):
        document_key = RREsMappingModifier.get_mapping_property()
        # original_must_filter = search_query.dsl["bool"]["must"]
        search_query.dsl["bool"]["must"] = []
        search_query.must(
            Match(
                field=document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        # for must_element in original_must_filter:
        #     search_query.must(
        #         RREsMappingModifier.create_nested_custom_filter(term, must_element)
        #     )

        # original_must_filter = search_query.dsl["bool"]["must_not"]
        # search_query.dsl["bool"]["must_not"] = []
        # for must_element in original_must_filter:
        #     search_query.must_not(
        #         RREsMappingModifier.create_nested_custom_filter(term, must_element)
        #     )

    @staticmethod
    def get_mapping_definition():
        """
        Defines the ES structure of the custom search document section. Called when the initial ES resources index is created.

        :return: dict of the custom document section
        :rtype dict
        """
        return {
            "type": "text",
            "fields": {
                "raw": {"type": "keyword", "ignore_above": 256},
                "folded": {"type": "text", "analyzer": "folding"},
            },
        }

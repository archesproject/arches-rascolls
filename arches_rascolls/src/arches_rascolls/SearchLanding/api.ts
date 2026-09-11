import { generateArchesURL } from "@/arches_vue_components/application";
import { fetchSearchDefinitionCounts } from "@/arches_search/SearchLanding/api.ts";
import {
    buildRequestQuery,
    buildRequestTerms,
    parseSearchDefinition,
} from "@/arches_search/SimpleSearch/utils/search-definition.ts";

import type { FeaturedItem } from "@/arches_rascolls/SearchLanding/types.ts";

export async function fetchFeaturedItems(): Promise<FeaturedItem[]> {
    const response = await fetch(
        generateArchesURL("arches_rascolls:api-featured-items"),
    );
    if (!response.ok) {
        throw new Error(response.statusText);
    }
    const data = await response.json();
    return data.results;
}

export async function fetchFeaturedItemCounts(
    items: FeaturedItem[],
): Promise<Record<string, number | null>> {
    return await fetchSearchDefinitionCounts(
        items.map((item) => {
            const searchDefinition = parseSearchDefinition(
                item.search_definition,
            );
            return {
                id: item.id,
                body: {
                    terms: buildRequestTerms(searchDefinition.terms),
                    query: buildRequestQuery(
                        Object.values(searchDefinition.queries),
                    ),
                    graphIds: searchDefinition.graphIds,
                    mapFilter: searchDefinition.mapFilter,
                },
            };
        }),
    );
}

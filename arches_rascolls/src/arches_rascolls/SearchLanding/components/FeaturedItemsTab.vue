<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";
import { useRouter } from "vue-router";

import Button from "primevue/button";
import Skeleton from "primevue/skeleton";

import { getGraphs } from "@/arches_search/AdvancedSearch/api.ts";
import {
    fetchFeaturedItemCounts,
    fetchFeaturedItems,
} from "@/arches_rascolls/SearchLanding/api.ts";
import { routeNames } from "@/arches_search/routes.ts";
import { usePendingSearchStore } from "@/arches_search/stores/usePendingSearchStore.ts";
import { parseSearchDefinition } from "@/arches_search/SimpleSearch/utils/search-definition.ts";

import type { FeaturedItem } from "@/arches_rascolls/SearchLanding/types.ts";
import type { GraphModel } from "@/arches_search/AdvancedSearch/types.ts";

const DEFAULT_FEATURED_ITEM_ICON = "pi-star";

const { $gettext } = useGettext();
const router = useRouter();

const featuredItems = ref<FeaturedItem[]>([]);
const hasLoadError = ref(false);
const featuredItemCounts = ref<Record<string, number | null>>({});
const featuredItemCountsLoaded = ref(false);
const resourceTypesById = ref<Record<string, GraphModel>>({});

const featuredItemGraphs = computed<Record<string, GraphModel[]>>(() =>
    Object.fromEntries(
        featuredItems.value.map((featuredItem) => [
            featuredItem.id,
            parseSearchDefinition(
                featuredItem.search_definition,
            ).graphIds.flatMap((graphId) => {
                const resourceType = resourceTypesById.value[graphId];
                return resourceType ? [resourceType] : [];
            }),
        ]),
    ),
);

onMounted(async () => {
    await Promise.all([loadFeaturedItems(), loadResourceTypes()]);
});

async function loadFeaturedItems(): Promise<void> {
    try {
        hasLoadError.value = false;
        featuredItems.value = await fetchFeaturedItems();
    } catch (error) {
        console.error(error);
        featuredItems.value = [];
        hasLoadError.value = true;
        return;
    }
    await loadFeaturedItemCounts();
}

async function loadFeaturedItemCounts(): Promise<void> {
    try {
        featuredItemCounts.value = await fetchFeaturedItemCounts(
            featuredItems.value,
        );
    } catch (error) {
        console.error(error);
        featuredItemCounts.value = Object.fromEntries(
            featuredItems.value.map((featuredItem) => [featuredItem.id, null]),
        );
    } finally {
        featuredItemCountsLoaded.value = true;
    }
}

async function loadResourceTypes(): Promise<void> {
    try {
        const graphs: GraphModel[] = await getGraphs();
        resourceTypesById.value = Object.fromEntries(
            graphs.map((graph) => [graph.graphid, graph]),
        );
    } catch (error) {
        console.error(error);
    }
}

function onSelectFeaturedItem(featuredItem: FeaturedItem): void {
    usePendingSearchStore().set({
        searchDefinition: featuredItem.search_definition,
    });
    router.push({ name: routeNames.simpleSearch });
}

function getFeaturedItemIconStyle(
    featuredItem: FeaturedItem,
): Record<string, string> | undefined {
    let iconStyle: Record<string, string> | undefined = undefined;
    if (featuredItem.color) {
        iconStyle = { background: featuredItem.color };
    }
    return iconStyle;
}
</script>

<template>
    <div class="featured-items-tab">
        <div class="featured-items-grid">
            <Button
                v-for="featuredItem in featuredItems"
                :key="featuredItem.id"
                class="featured-item-card"
                :aria-label="featuredItem.label"
                severity="secondary"
                type="button"
                variant="outlined"
                @click="onSelectFeaturedItem(featuredItem)"
            >
                <div class="featured-item-header">
                    <div
                        class="featured-item-icon-tile"
                        :style="getFeaturedItemIconStyle(featuredItem)"
                    >
                        <i
                            class="pi"
                            :class="
                                featuredItem.icon || DEFAULT_FEATURED_ITEM_ICON
                            "
                        />
                    </div>
                    <div class="featured-item-identity">
                        <div class="featured-item-count">
                            <Skeleton
                                v-if="!featuredItemCountsLoaded"
                                width="4rem"
                                height="2.2rem"
                            />
                            <span
                                v-else-if="
                                    featuredItemCounts[featuredItem.id] === null
                                "
                                class="featured-item-count-unavailable"
                            >
                                {{ $gettext("Unavailable") }}
                            </span>
                            <span v-else>
                                {{ featuredItemCounts[featuredItem.id] }}
                            </span>
                        </div>
                        <div class="featured-item-label">
                            {{ featuredItem.label }}
                        </div>
                    </div>
                </div>
                <p
                    v-if="featuredItem.description"
                    class="featured-item-description"
                >
                    {{ featuredItem.description }}
                </p>

                <div
                    v-if="featuredItemGraphs[featuredItem.id]?.length"
                    class="featured-item-graphs"
                >
                    <span
                        v-for="graph in featuredItemGraphs[featuredItem.id]"
                        :key="graph.graphid"
                        class="featured-item-graph-pill"
                    >
                        <i
                            v-if="graph.iconclass"
                            :class="graph.iconclass"
                        />
                        <span>{{ graph.name }}</span>
                    </span>
                </div>
            </Button>
        </div>

        <span
            v-if="hasLoadError"
            aria-live="polite"
            class="load-error"
            role="status"
        >
            {{ $gettext("Featured items are unavailable.") }}
        </span>
    </div>
</template>

<style scoped>
.featured-items-tab {
    --arches-search-featured-card-radius: 1.2rem;
}

.featured-items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(26rem, 1fr));
    gap: 1.2rem;
}

.featured-items-tab .featured-item-card {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start !important;
    gap: 1rem;
    padding: 1.6rem 1.8rem 2rem;
    border: 0.1rem solid var(--arches-search-card-border);
    border-radius: var(--arches-search-featured-card-radius);
    background: var(--arches-search-card-bg);
    color: var(--p-text-color) !important;
    text-align: left;
    transition:
        box-shadow 0.15s,
        transform 0.15s,
        border-color 0.15s;
}

.featured-items-tab .featured-item-card:hover,
.featured-items-tab .featured-item-card:focus-visible {
    background: var(--arches-search-card-bg) !important;
    border-color: var(--p-primary-color) !important;
    box-shadow: var(--arches-search-card-shadow-hover);
    transform: translateY(-0.2rem);
}

.featured-item-header {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}

.featured-item-icon-tile {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    inline-size: 3.8rem;
    block-size: 3.8rem;
    border-radius: var(--arches-search-model-icon-radius);
    background: var(--p-primary-color);
    color: var(--p-surface-0);
    font-size: 1.6rem;
}

.featured-item-icon-tile .pi {
    font-size: 1.6rem !important;
}

.featured-item-identity {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
}

.featured-item-count {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    color: var(--p-text-color);
}

.featured-item-count-unavailable {
    font-size: var(--p-arches-search-font-size);
    font-weight: 600;
    color: var(--p-text-muted-color);
}

.featured-item-label {
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1.2;
    color: var(--p-text-color);
}

.featured-item-description {
    margin: 0;
    padding-block-start: 1rem;
    border-block-start: 0.1rem solid var(--arches-search-card-border);
    font-size: 1.2rem;
    line-height: 1.55;
    color: var(--p-text-muted-color);
}

.featured-item-graphs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.featured-item-graph-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.2rem 0.8rem;
    border-radius: var(--arches-search-radius-pill);
    background: var(--arches-search-primary-muted-bg);
    color: var(--p-primary-color);
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.featured-item-graph-pill .pi {
    font-size: 1rem !important;
}

.load-error {
    display: block;
    margin-top: 1rem;
    color: var(--p-surface-500);
    font-size: var(--p-arches-search-font-size);
}
</style>

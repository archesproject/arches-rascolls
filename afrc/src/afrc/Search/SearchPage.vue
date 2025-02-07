<script setup lang="ts">
import { onMounted, ref, watch, provide } from "vue";
import type { Ref } from "vue";
import { useGettext } from "vue3-gettext";

import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import DataView from "primevue/dataview";

import { DEFAULT_ERROR_TOAST_LIFE, ERROR } from "@/afrc/Search/constants.ts";

import arches from "arches";

import SimpleSearchFilter from "@/afrc/Search/components/SimpleSearchFilter.vue";
import SearchResultItem from "@/afrc/Search/components/SearchResultItem.vue";
import SearchItemDetails from "@/afrc/Search/components/SearchItemDetails.vue";
import InteractiveMap from "@/afrc/Search/components/InteractiveMap/InteractiveMap.vue";
import { fetchMapData } from "@/afrc/Search/api.ts";
import type { GenericObject } from "@/afrc/Search/types";
import type { Basemap, MapLayer, MapSource } from "@/afrc/Search/types.ts";

let query = getQueryObject(null);
let queryString = ref(JSON.stringify(query));
let searchResults = ref([]);
let resultsCount = ref("calculating...");
let resultSelected = ref("");
let forcePaginatorRepaint = ref(0);
const showMap = ref(false);
const basemaps: Ref<Basemap[]> = ref([]);
const overlays: Ref<MapLayer[]> = ref([]);
const sources: Ref<MapSource[]> = ref([]);
const resultsSelected: Ref<string[]> = ref([]);
const dataLoaded = ref(false);
const newQuery = ref(false);
const toast = useToast();
const { $gettext } = useGettext();

provide("resultsSelected", resultsSelected);
provide("resultSelected", resultSelected);

watch(queryString, () => {
    performSearch();
});

function updateFilter(componentName: string, value: object) {
    console.log(value);
    newQuery.value = true;
    // Test for an empty object
    function isEmpty(value: unknown) {
        if (value === null || value === undefined) {
            return true;
        }

        if (typeof value === "string") {
            return value.trim() === "";
        }

        if (Array.isArray(value)) {
            return value.length === 0;
        }

        if (typeof value === "object") {
            return Object.keys(value).length === 0;
        }

        return false;
    }

    if (isEmpty(value)) {
        delete query[componentName];
    } else {
        query[componentName] = value;
    }
    queryString.value = JSON.stringify(query);
}

function getQueryObject(uri: string | null): GenericObject {
    const url = new URL(uri || location.href);
    const params = new URLSearchParams(url.search);
    const obj: GenericObject = {};

    for (const [key, value] of params.entries()) {
        obj[key] = value;
    }

    return obj;
}

async function performSearch() {
    const queryObj = JSON.parse(queryString.value ?? "{}");

    Object.keys(queryObj).forEach((key) => {
        queryObj[key] = JSON.stringify(queryObj[key]);
    });

    if (newQuery.value) {
        const componentName = "paging-filter";
        delete queryObj[componentName];
        forcePaginatorRepaint.value += 1;
        newQuery.value = false;
    }

    const qs = new URLSearchParams(queryObj);

    fetch(arches.urls["api-search"] + "?" + qs.toString())
        .then((response) => response.json())
        .then((data) => {
            const hits: never[] = data.results.hits.hits;
            searchResults.value = hits;
            resultsCount.value = data.total_results;
            resultsSelected.value = [];
        });
}

async function fetchSystemMapData() {
    try {
        const mapData = await fetchMapData();
        const layers = mapData.map_layers;

        // omit search results layer for now
        overlays.value = layers.filter(
            (layer: MapLayer) =>
                layer.isoverlay &&
                layer.maplayerid !== "6b9d3c6a-60a4-4630-b4f8-4c5159b68cec",
        );

        layers
            .filter((layer: MapLayer) => !layer.isoverlay)
            .forEach((layer: MapLayer) => {
                basemaps.value.push({
                    name: layer.name,
                    active: layer.addtomap,
                    value: layer.name,
                    id: layer.name,
                    url: "https://tiles.openfreemap.org/styles/positron",
                });
            });

        sources.value = mapData.map_sources;
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to fetch map data."),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
}

async function onPageChange(event: {
    first: number;
    rows: number;
    page: number;
    pageCount: number;
}) {
    console.log("onPageChange");
    console.log(queryString.value);
    const componentName = "paging-filter";
    query[componentName] = event.page + 1;
    queryString.value = JSON.stringify(query);
    console.log(queryString.value);
}

onMounted(async () => {
    performSearch();
    await fetchSystemMapData();
    dataLoaded.value = true;
});
</script>

<template>
    <div class="afrc-container">
        <!-- Main Content Section -->
        <header>
            <SimpleSearchFilter
                style="flex-grow: 1; max-width: 800px"
                :update-filter
            />
            <div class="view-buttons">
                <Button
                    :class="{ active: !showMap }"
                    label="terms"
                    severity="secondary"
                    icon="pi pi-file"
                    icon-pos="top"
                    :outlined="!showMap"
                    @click="showMap = false"
                />
                <Button
                    :class="{ active: showMap }"
                    label="map"
                    severity="secondary"
                    icon="pi pi-map"
                    icon-pos="top"
                    :outlined="showMap"
                    @click="showMap = true"
                />
            </div>
        </header>

        <main>
            <section class="afrc-search-results-panel">
                <div class="result-count">{{ resultsCount }} Results</div>
                <div class="search-result-list">
                    <!-- <div style="height: 50px">{{ item?._source.displayname }}</div> -->
                    <DataView
                        :key="forcePaginatorRepaint"
                        lazy
                        paginator
                        rows="5"
                        :value="searchResults"
                        :total-records="resultsCount"
                        @page="onPageChange"
                    >
                        <template #list="slotProps">
                            <SearchResultItem
                                v-for="item in slotProps.items"
                                :key="item"
                                :search-result="item"
                            />
                        </template>
                    </DataView>
                </div>
            </section>
            <section v-if="dataLoaded && resultSelected">
                <SearchItemDetails :instance-id="resultSelected" />
            </section>
            <div
                v-if="showMap && dataLoaded"
                style="width: 100%; height: 100%"
            >
                <InteractiveMap
                    :basemaps="basemaps"
                    :overlays="overlays"
                    :sources="sources"
                    :include-drawer="false"
                    :popup-enabled="false"
                />
            </div>

            <aside v-if="!showMap">
                <div>Search Facets</div>
                <section class="facets">
                    <div class="facet-item selected">
                        <p>Reference Objects</p>
                        <p>
                            Items in our reference collection, such as papers,
                            paints, textiles, and other items
                        </p>
                        <a href="#">click to unselect</a>
                    </div>
                    <div class="facet-item">
                        <p>Samples</p>
                        <p>
                            Materials removed from works of art or other
                            reference objects
                        </p>
                        <a href="#">click to select</a>
                    </div>
                    <div class="facet-item">
                        <p>Building Materials</p>
                        <p>Construction materials and related objects</p>
                        <a href="#">click to select</a>
                    </div>
                </section>
            </aside>
        </main>
    </div>

    <Toast />
</template>

<style scoped>
:root {
    font-size: 16px;
}

.afrc-container {
    font-family: Arial, sans-serif;
    background-color: #f8f8f8;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

main {
    display: flex;
    flex-direction: row;
    flex-grow: 1;
}

header {
    font-size: 2rem;
    display: flex;
    border-bottom: 1px #ccc solid;
    padding: 5px;
}

.view-buttons {
    display: flex;
    gap: 5px;
    margin-left: 20px;
}

section.afrc-search-results-panel {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    margin: 15px;
    overflow-y: auto;
    height: calc(100vh - 150px);
    min-width: 350px;
}

.search-result-list {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    gap: 20px;
}

.result-count {
    font-size: 1.6rem;
    margin: 0px;
    margin-bottom: 15px;
}

aside {
    max-width: 25%;
    border-left: 1px #ccc solid;
    padding: 15px;
}

.facets {
    padding: 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.facet-item {
    font-size: 1rem;
    padding: 16px;
    border: 1px solid #ddd;
    text-align: center;
    cursor: pointer;
    max-width: 15rem;
    min-height: 15rem;
}

.facet-item.selected {
    background-color: #f0f8ff;
    border-color: #007bff;
}
</style>

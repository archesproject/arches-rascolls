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
import type { Feature } from "maplibre-gl/dist/maplibre-gl";

let query = getQueryObject(null);
let queryString = ref(JSON.stringify(query));
let searchResults = ref([]);
let resultsCount = ref();
let resultSelected = ref("");
let zoomToFeature = ref("");
let highlightResult = ref("");
let spatialFilter: Ref<Feature[]> = ref([]);
let forcePaginatorRepaint = ref(0);
const showMap = ref(false);
const basemaps: Ref<Basemap[]> = ref([]);
const overlays: Ref<MapLayer[]> = ref([]);
const sources: Ref<MapSource[]> = ref([]);
const resultsSelected: Ref<string[]> = ref([]);
const dataLoaded = ref(false);
const loadingSearchResults = ref(true);
const pageSize = ref();
const newQuery = ref(true);
const searchid = ref();
const toast = useToast();
const { $gettext } = useGettext();

provide("resultsSelected", resultsSelected);
provide("resultSelected", resultSelected);
provide("zoomToFeature", zoomToFeature);
provide("highlightResult", highlightResult);
provide("showMap", showMap);

watch(queryString, () => {
    performSearch();
});

function uniqueId() {
    /* Not cryptographically secure, but good enough for Vue component keys. */
    return Math.floor(Math.random() * Date.now());
}

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
    loadingSearchResults.value = true;
    const queryObj = JSON.parse(queryString.value ?? "{}");

    Object.keys(queryObj).forEach((key) => {
        queryObj[key] = JSON.stringify(queryObj[key]);
    });

    if (newQuery.value) {
        const componentName = "paging-filter";
        delete queryObj[componentName];
        searchid.value = uniqueId();
        forcePaginatorRepaint.value += 1;
        newQuery.value = false;
    }

    queryObj["searchid"] = searchid.value;

    const qs = new URLSearchParams(queryObj);

    fetch(arches.urls["api-search"] + "?" + qs.toString())
        .then((response) => response.json())
        .then((data) => {
            const hits: never[] = data.results.hits.hits;
            searchResults.value = hits;
            resultsCount.value = data.total_results;
            pageSize.value = data.page_size;
            resultsSelected.value = [];
            loadingSearchResults.value = false;
        });
}

const updateDrawnFeaturesGeometry = function (features: Feature[]) {
    spatialFilter.value = features;
    console.log("update the query with these feature(s): ", features);

    newQuery.value = true;
    const componentName = "map-filter";

    if (features.length === 0) {
        delete query[componentName];
    } else {
        query[componentName] = features;
    }
    queryString.value = JSON.stringify(query);
};

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

        overlays.value.sort((a, b) => (b.sortorder ?? 0) - (a.sortorder ?? 0));
        mapData.rascolls_basemaps.forEach((layer: MapLayer) => {
            basemaps.value.push({
                name: layer.title,
                active: layer.addtomap,
                value: layer.name,
                id: layer.name,
                url: layer.url,
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
                    :style="{ fontSize: '.75em', borderRadius: '3px' }"
                    label="Terms"
                    size="large"
                    severity="secondary"
                    icon="pi pi-file"
                    icon-pos="left"
                    :outlined="!showMap"
                    @click="showMap = false"
                />
                <Button
                    :class="{ active: showMap }"
                    :style="{ fontSize: '.75em', borderRadius: '3px' }"
                    label="Map"
                    size="large"
                    severity="secondary"
                    icon="pi pi-map"
                    icon-pos="left"
                    :outlined="showMap"
                    @click="showMap = true"
                />
            </div>
        </header>

        <main>
            <section
                class="afrc-search-results-panel"
                :class="{ 'map-sidebar': showMap }"
            >
                <div
                    v-if="loadingSearchResults"
                    class="section-header"
                >
                    {{ $gettext("Loading Results...") }}
                </div>
                <div
                    v-else
                    class="section-header"
                >
                    {{ resultsCount }} Results
                </div>
                <div class="search-result-list">
                    <DataView
                        :key="forcePaginatorRepaint"
                        data-key="id"
                        lazy
                        paginator
                        :rows="pageSize"
                        :value="searchResults"
                        :total-records="resultsCount"
                        @page="onPageChange"
                    >
                        <template #list="slotProps">
                            <div v-if="loadingSearchResults">
                                <SearchResultItem
                                    v-for="i in 5"
                                    :key="i"
                                    :search-result="{}"
                                    :loading="true"
                                />
                            </div>
                            <div v-else>
                                <SearchResultItem
                                    v-for="item in slotProps.items"
                                    :key="item"
                                    :search-result="item"
                                    :loading="false"
                                />
                            </div>
                        </template>
                    </DataView>
                </div>
            </section>
            <section v-if="dataLoaded && resultSelected">
                <SearchItemDetails :instance-id="resultSelected" />
            </section>
            <div
                v-if="showMap && dataLoaded"
                style="width: 100%; height: inherit"
            >
                <InteractiveMap
                    :basemaps="basemaps"
                    :overlays="overlays"
                    :sources="sources"
                    :include-drawer="true"
                    :query="searchResults"
                    :popup-enabled="false"
                    @drawn-features-updated="updateDrawnFeaturesGeometry"
                />
            </div>

            <aside v-if="!showMap">
                <div>
                    <h1 class="section-header">Search Facets</h1>
                    <p class="section-tag">
                        Select the Collections that you want to include in your
                        search
                    </p>
                </div>
                <section class="facets">
                    <div class="facet-item selected">
                        <div class="facet-item-icon pi pi-address-book"></div>
                        <h2 class="facet-item-title">Reference Objects</h2>
                        <p class="facet-item-tag">
                            Reference collection items such as papers, paints,
                            textiles
                        </p>
                        <a
                            class="facet-item-toggle"
                            href="#"
                            >(click to unselect)</a
                        >
                    </div>
                    <div class="facet-item">
                        <div class="facet-item-icon pi pi-chart-line"></div>
                        <h2 class="facet-item-title">Samples</h2>
                        <p class="facet-item-tag">
                            Materials removed from works of art or other
                            reference objects
                        </p>
                        <a
                            class="facet-item-toggle"
                            href="#"
                            >(click to select)</a
                        >
                    </div>
                    <div class="facet-item">
                        <div class="facet-item-icon pi pi-building"></div>
                        <h2 class="facet-item-title">Building Materials</h2>
                        <p class="facet-item-tag">
                            Construction materials and related objects
                        </p>
                        <a
                            class="facet-item-toggle"
                            href="#"
                            >(click to select)</a
                        >
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
    background: #fafafa;
}

.section-header {
    font-size: 1.33em;
    font-weight: 500;
    color: #25476a;
    margin-top: 0px;
    margin-bottom: 3px;
}

.afrc-search-results-panel.map-sidebar .section-header {
    font-size: 1.33em;
    font-weight: 500;
    color: #25476a;
    margin-bottom: 0px;
}

.afrc-search-results-panel.map-sidebar .search-result-list {
    margin-left: -15px;
    margin-right: -15px;
    margin-top: 13px;
    gap: 0px;
}

.section-tag {
    font-size: 1em;
    font-weight: 300;
    color: #888;
    line-height: 1.5;
    margin: 0px;
}
.p-autocomplete-input-multiple {
    border-radius: 3px;
}

.view-buttons {
    display: flex;
    gap: 5px;
    margin-left: 20px;
}
.view-buttons button {
    border-color: #ddd;
    width: 100px;
}
.view-buttons button.active {
    background: #fff;
}
.p-button-label {
    font-size: 0.5em;
}
section.afrc-search-results-panel {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    padding: 15px;
    overflow-y: auto;
    height: calc(
        100vh - 50px
    ); /* for display in a standalone plugin or embedded in AFS */
    min-width: 400px;
    background: #fff;
}

/* 
The following rule is for display in as a standard plugin within RASColls.
.base-manager-grid is an arches class, so this rule won't apply
in a standalone plugin or when embedded in AFS.
*/
.base-manager-grid section.afrc-search-results-panel {
    height: calc(100vh - 100px);
}

.search-result-list {
    margin-top: 10px;
    margin-left: -15px;
    margin-right: -15px;
    display: flex;
    flex-direction: column;
    border-top: 1px solid #ddd;
    gap: 0px;
}

.map-sidebar .search-result-list {
    border-top: 1px solid #ddd;
}

aside {
    width: 420px;
    background: #fdfdfd;
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
    padding: 15px;
    border: 1px solid #ddd;
    background: #fdfdfd;
    text-align: center;
    cursor: pointer;
    width: 170px;
    height: 170px;
    border-radius: 3px;
}
.facet-item:hover {
    background-color: #f0f8ff;
    border-color: #007bff;
}

.facet-item.selected {
    background-color: #f0f8ff;
    border-color: #007bff;
    filter: drop-shadow(2px 2px 3px #ccc);
}
.facet-item-title {
    font-size: 1.05em;
    font-weight: 300;
    color: #25476a;
    margin: 0px;
}
.facet-item-icon {
    font-size: 18px;
    padding: 11px;
    border: 1px solid #aaa;
    border-radius: 50%;
    color: #aaa;
    background: #eee;
    margin-bottom: 10px;
    height: 40px;
    width: 40px;
}
.facet-item.selected .facet-item-icon {
    border: 1px solid #244768;
    border-radius: 50%;
    color: #244768;
    background: #98adc2;
}
.facet-item-tag {
    font-size: 0.85em;
    color: #aaa;
    line-height: 1.15;
    margin: 0px;
}
.facet-item-toggle {
    color: #007bff;
    font-size: 0.75em;
}
</style>

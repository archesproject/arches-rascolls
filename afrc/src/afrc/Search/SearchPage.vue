<script setup lang="ts">
import { onMounted, ref, watch, provide } from "vue";
import type { Ref } from "vue";
import { useGettext } from "vue3-gettext";

import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
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
let resultsCount = ref("calculating...");
let resultSelected = ref("");
let spatialFilter: Ref<Feature[]> = ref([]);
const showMap = ref(false);
const basemaps: Ref<Basemap[]> = ref([]);
const overlays: Ref<MapLayer[]> = ref([]);
const sources: Ref<MapSource[]> = ref([]);
const resultsSelected: Ref<string[]> = ref([]);
const dataLoaded = ref(false);
const toast = useToast();
const { $gettext } = useGettext();

provide("resultsSelected", resultsSelected);
provide("resultSelected", resultSelected);

watch(queryString, () => {
    doQuery();
});

function updateFilter(componentName: string, value: object) {
    console.log(value);
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

const doQuery = function () {
    const queryObj = JSON.parse(queryString.value ?? "{}");

    Object.keys(queryObj).forEach((key) => {
        queryObj[key] = JSON.stringify(queryObj[key]);
    });

    const qs = new URLSearchParams(queryObj);

    fetch(arches.urls["api-search"] + "?" + qs.toString())
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            searchResults.value = data.results.hits.hits;
            resultsCount.value = data.total_results;
            resultsSelected.value = [];
        });
};

const updateDrawnFeaturesGeometry = function (features: Feature[]) {
    spatialFilter.value = features;
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

onMounted(async () => {
    doQuery();
    await fetchSystemMapData();
    dataLoaded.value = true;
});
</script>

<template>
    <div class="afrc-container">
        <!-- Main Content Section -->
        <header>
            <SimpleSearchFilter
                style="flex-grow: 1; max-width: 800px;"
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
            <section class="afrc-search-results-panel"
                :class="{ 'map-sidebar' : showMap}"
            >
                <div class="section-header">{{ resultsCount }} Results</div>
                <div class="search-result-list">
                    <SearchResultItem
                        v-for="searchResult in searchResults"
                        :key="searchResult"
                        :search-result
                    />
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
                    :include-drawer="true"
                    :popup-enabled="false"
                    @drawn-features-updated="
                    (features) => {
                        updateDrawnFeaturesGeometry(
                            features,
                        );
                    }
                "
                />
            </div>

            <aside v-if="!showMap">
                <div>
                    <h1 class="section-header">Search Facets</h1>
                    <p class="section-tag">Select the Collections that you want to include in your search</p>
                </div>
                <section class="facets">
                    <div class="facet-item selected">
                        <div class="facet-item-icon pi pi-address-book"></div>
                        <h2 class="facet-item-title">Reference Objects</h2>
                        <p class="facet-item-tag">
                            Reference collection items such as papers,
                            paints, textiles
                        </p>
                        <a class="facet-item-toggle" href="#">(click to unselect)</a>
                    </div>
                    <div class="facet-item">
                        <div class="facet-item-icon pi pi-chart-line"></div>
                        <h2 class="facet-item-title">Samples</h2>
                        <p class="facet-item-tag">
                            Materials removed from works of art or other
                            reference objects
                        </p>
                        <a class="facet-item-toggle" href="#">(click to select)</a>
                    </div>
                    <div class="facet-item">
                        <div class="facet-item-icon pi pi-building"></div>
                        <h2 class="facet-item-title">Building Materials</h2>
                        <p class="facet-item-tag">Construction materials and related objects</p>
                        <a class="facet-item-toggle" href="#">(click to select)</a>
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
    height: 100vh;
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
    font-size: .5em;
}
section.afrc-search-results-panel {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    padding: 15px;
    overflow-y: auto;
    width: 400px;
    min-width: 400px;
    background: #fff;
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
    background: #98ADC2;
}
.facet-item-tag {
    font-size: 0.85em;
    color: #aaa;
    line-height: 1.15;
    margin: 0px;
}
.facet-item-toggle {
    color:#007bff;
    font-size: 0.75em;
}
</style>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import type { Ref } from "vue";
import { useGettext } from "vue3-gettext";

import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
} from "@/afrc/Search/constants.ts";

import SimpleSearchFilter from "@/afrc/Search/components/SimpleSearchFilter.vue";
import SearchResultItem from "@/afrc/Search/components/SearchResultItem.vue";
import InteractiveMap from "@/afrc/Search/components/InteractiveMap/InteractiveMap.vue";
import { fetchMapData } from "@/afrc/Search/api.ts";
import type { GenericObject } from "@/afrc/Search/types";
import type {
    Basemap,
    MapLayer,
    MapSource,
} from "@/afrc/Search/types.ts";

let query = getQueryObject(null);
let queryString = ref(JSON.stringify(query));
let searchResults = ref([]);
let resultsCount = ref("calculating...");
const showMap = ref(false);
const basemaps: Ref<Basemap[]> = ref([]);
const overlays: Ref<MapLayer[]> = ref([]);
const sources: Ref<MapSource[]> = ref([]);
const dataLoaded = ref(false);
const toast = useToast();
const { $gettext } = useGettext();

watch(queryString, () => {
    doQuery();
});

function updateFilter(componentName: string, value: object) {
    console.log(value);
    // Test for an empty object
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    function isEmpty(value: any) {
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

    fetch("search/resources" + "?" + qs.toString())
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            searchResults.value = data.results.hits.hits;
            resultsCount.value = data.total_results;
        });

    // self.updateRequest = $.ajax({
    //     type: "GET",
    //     url: arches.urls.search_results,
    //     data: queryObj,
    //     context: this,
    //     success: function(response) {
    //         _.each(this.sharedStateObject.searchResults, function(value, key, results) {
    //             if (key !== "timestamp") {
    //                 delete this.sharedStateObject.searchResults[key];
    //             }
    //         }, this);
    //         _.each(response, function(value, key, response) {
    //             if (key !== "timestamp") {
    //                 this.sharedStateObject.searchResults[key] = value;
    //             }
    //         }, this);
    //         this.sharedStateObject.searchResults.timestamp(response.timestamp);
    //         this.sharedStateObject.userIsReviewer(response.reviewer);
    //         this.sharedStateObject.userid(response.userid);
    //         this.sharedStateObject.total(response.total_results);
    //         this.sharedStateObject.hits(response.results.hits.hits.length);
    //         this.sharedStateObject.alert(false);
    //     },
    //     error: function(response, status, error) {
    //         const alert = new AlertViewModel("ep-alert-red", arches.translations.requestFailed.title, response.responseJSON?.message);
    //         if(self.updateRequest.statusText !== "abort"){
    //             this.alert(alert);
    //         }
    //         this.sharedStateObject.loading(false);
    //     },
    //     complete: function(request, status) {
    //         self.updateRequest = undefined;
    //         window.history.pushState({}, "", "?" + $.param(queryObj).split("+").join("%20"));
    //         this.sharedStateObject.loading(false);
    //     }
    // });
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

        layers.filter((layer: MapLayer) => !layer.isoverlay).forEach((layer: MapLayer) => {
            basemaps.value.push({name: layer.name, active: layer.addtomap, value: layer.name, id: layer.name});
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

onMounted(async () =>{
    doQuery();
    await fetchSystemMapData();
    dataLoaded.value = true;
});
</script>

<template>
    <div class="container">
        <!-- Main Content Section -->
        <header>
            <SimpleSearchFilter
                style="flex-grow: 1; max-width: 800px"
                :update-filter
            />
            <div class="view-buttons">
                <Button
                    :class="{ active: !showMap }"
                    variant="outlined"
                    label="terms"
                    icon="pi pi-file"
                    icon-pos="top"
                    @click="showMap = false"
                />
                <Button
                    :class="{ active: showMap }"
                    variant="outlined"
                    label="map"
                    icon="pi pi-map"
                    icon-pos="top"
                    @click="showMap = true"
                />
            </div>
        </header>

        <main>
            <section class="search-results-panel">
                <div class="result-count">{{ resultsCount }} Results</div>
                <div class="search-result-list">
                    <SearchResultItem
                        v-for="searchResult in searchResults"
                        :key="searchResult"
                        :search-result
                    />
                </div>
            </section>

            <div
                v-if="showMap && dataLoaded"
                style="width: 100%; height: 100%"
            >
                <InteractiveMap
                    :basemaps="basemaps"
                    :overlays="overlays"
                    :sources="sources"
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
.container {
    font-family: Arial, sans-serif;
    background-color: #f8f8f8;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
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
}
.view-buttons {
    display: flex;
    gap: 5px;
    margin-left: 20px;
}
.search-results-panel {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    margin: 15px;
    overflow-y: auto;
}
.search-result-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.result-count {
    font-size: 1rem;
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
    font-size: 0.7rem;
    padding: 16px;
    border: 1px solid #ddd;
    text-align: center;
    cursor: pointer;
    max-width: 11rem;
    min-height: 11rem;
}
.facet-item.selected {
    background-color: #f0f8ff;
    border-color: #007bff;
}
</style>

<script setup lang="ts">
import { onMounted, inject, ref, watch } from "vue";
import type { UnspecifiedObject, GenericObject } from "@/afrc/Search/types";
import { fetchResourceData, fetchImageData } from "@/afrc/Search/api.ts";
import type { Ref } from "vue";
import Button from "primevue/button";
import Carousel from "primevue/carousel";

const resultSelected = inject("resultSelected") as Ref<string>;
const resultsSelected = inject("resultsSelected") as Ref<string[]>;
const zoomFeature = inject("zoomFeature") as GenericObject;
const showMap = inject("showMap") as Ref<string>;

const displayname: Ref<string> = ref("");
const displaydescription: Ref<string> = ref("");
const images: Ref<string[]> = ref([]);
const acquisitions: Ref<Acquisition[]> = ref([]);
const composition: Ref<Composition[]> = ref([]);
const identifier: Ref<string> = ref("");
const hasGeom: Ref<boolean> = ref(false);
const placeNames: Ref<GenericObject[]> = ref([]);

interface Acquisition {
    person: string;
    date: number;
    details: string;
}

interface Composition {
    type: string;
    mixture: string;
}

onMounted(async () => {
    getData();
});

watch(resultSelected, () => {
    getData();
});

watch(showMap, () => {
    clearResult();
});

async function getData() {
    const resp = await fetchResourceData(resultSelected.value);
    const imageResourceids = resp.resource["Digital Reference"]?.map(
        (tile: UnspecifiedObject) =>
            (tile["Digital Source"] as UnspecifiedObject)?.["resourceId"],
    );
    const accessionNumber = resp.resource["Identifier"]?.find(
        (identifier: UnspecifiedObject) =>
            (identifier[
                "Identifier_type"
            ] as UnspecifiedObject["@display_value"]) === "Accession Number",
    );
    hasGeom.value =
        !!resp.resource["Production "]?.[0]["Production_location"]?.[
            "Production_location_geo"
        ]?.geojson;
    placeNames.value = resp.resource["Production "]?.[0][
        "Production_location"
    ]?.["instance_details"].map((place: GenericObject) => ({
        name: place.display_value,
        resourceid: place.resourceId,
    }));
    acquisitions.value = resp.resource["Addition to Collection"]?.map(
        (tile: GenericObject) => ({
            person: tile?.["Addition to Collection_carried out by"][
                "@display_value"
            ],
            date: tile?.["Addition to Collection_time"][
                "Addition to Collection_time_begin of the begin"
            ]["@display_value"],
            details: tile?.["Addition to Collection_Statement"]
                ?.map(
                    (statement: GenericObject) =>
                        statement?.[
                            "Addition to Collection_Statement_content"
                        ]?.["@display_value"],
                )
                .join(" "),
        }),
    );
    composition.value = [
        {
            type: resp.resource["material"]?.["@display_value"],
            mixture: resp.resource["mixture type"]?.["@display_value"],
        },
    ];
    displayname.value = resp.displayname;
    const descriptionValue = resp.resource["Statement"]?.map(
        (statement: GenericObject) =>
            `${statement?.["Statement_content"]?.["@display_value"]}`,
    );
    displaydescription.value = descriptionValue ? descriptionValue.join("<br>") : descriptionValue;
    identifier.value = accessionNumber
        ? accessionNumber["Identifier_content"]["@display_value"]
        : "";

    if (imageResourceids) {
        images.value = await fetchImageData(imageResourceids);
    } else {
        images.value = [];
    }
}

function clearResult() {
    resultSelected.value = "";
    resultsSelected.value = [];
}

function zoomToSearchResult(resourceid: string, action: string) {
    zoomFeature.value = {resourceid, action};
}
</script>

<template>
    <div class="search-item-details">
        <div class="title">
            <div style="display: flex; flex-direction: column; padding: 3px">
                <div>
                    {{ displayname || "No name provided" }}
                </div>
                <div class="current-location">
                    {{ identifier }}
                </div>
            </div>
            <div>
                <Button
                    class="close-button"
                    label="Close"
                    severity="secondary"
                    icon="pi pi-times-circle"
                    icon-pos="top"
                    text
                    size="large"
                    @click="clearResult()"
                />
            </div>
        </div>
        <div class="description">
            <div class="value-header">Description</div>
            <div class="resource-details-value">
                <template
                    v-if="
                        displaydescription && displaydescription != 'Undefined'
                    "
                >
                    <!-- eslint-disable-next-line vue/no-v-html -->
                    <div v-html="displaydescription"></div>
                </template>
                <div v-else>No description provided</div>
            </div>
        </div>
        <div
            class="value-header"
            style="padding: 0 10px"
        >
            Images
        </div>
        <div
            v-if="images.length"
            class="images"
        >
            <Carousel
                :value="images"
                :num-visible="1"
                :num-scroll="1"
                container-class="flex items-center"
            >
                <template #item="image">
                    <div
                        class="border border-surface-200 dark:border-surface-700 rounded m-2 p-4"
                    >
                        <div class="mb-4">
                            <div class="relative mx-auto">
                                <div class="carousel-image-container" style="padding: 3px">
                                    <img
                                        :src="image.data"
                                        class="w-full rounded carousel-image"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </Carousel>
        </div>
        <div
            v-else
            class="resource-details-value"
            style="padding: 0 13px"
        >
            <div>No images available</div>
        </div>
        <div
            class="resource-details"
            style="color: grey"
        >
            <div
                v-for="(material, index) in composition"
                :key="index"
            >
                <div class="value-header">Material Information</div>
                <div class="value-entry">
                    Materials:<span class="resource-details-value">{{
                        material.type || "No material type provided"
                    }}</span>
                </div>
                <div class="value-entry">
                    Mixture Type:<span class="resource-details-value">{{
                        material.mixture || "No mixture type provided"
                    }}</span>
                </div>
            </div>
        </div>
        <div class="resource-details">
            <div class="value-header">Acquisition Information</div>
            <div v-if="acquisitions">
                <div
                    v-for="(acquisition, index) in acquisitions"
                    :key="index"
                >
                    <div class="value-entry">
                        Acquired by:<span class="resource-details-value">{{
                            acquisition.person
                        }}</span>
                    </div>
                    <div class="value-entry">
                        Acquired on:<span class="resource-details-value">{{
                            acquisition.date
                        }}</span>
                    </div>
                    <div class="value-entry">
                        Acquisition Details:<span
                            class="resource-details-value"
                            >{{ acquisition.details }}</span
                        >
                    </div>
                </div>
            </div>
            <div
                v-else
                class="resource-details-value"
            >
                No acquisition information available
            </div>
        </div>
        <div class="resource-details">
            <div class="value-header">Analytic Data</div>
            <div class="value-entry">
                <span class="resource-details-value">No analytic data available</span>
            </div>
        </div>
        <div>
            <div class="resource-details">
                <div class="value-header">Associated Places</div>
                    <div v-if="placeNames?.length">
                        <div
                            v-for="place in placeNames"
                            :key="place.resourceid"
                            style="
                                display: flex;
                                flex-direction: row;
                                align-items: center;
                                justify-content: space-between;
                            "
                        >
                            <div class="value-entry">
                                <span
                                    class="resource-details-value"
                                    @click="console.log(place)"
                                    >{{ place.name }}</span
                                >
                            </div>
                            <div style="display: flex; flex-direction: row">
                                <div v-if="hasGeom && showMap">
                                    <Button
                                        class="action-button"
                                        label="Zoom to Place"
                                        severity="secondary"
                                        text
                                        icon="pi pi-map-marker"
                                        size="large"
                                        @click="
                                            zoomToSearchResult(place.resourceid, 'zoom')
                                        "
                                    />
                                </div>
                                <div v-if="hasGeom && showMap">
                                    <Button
                                        class="action-button"
                                        label="Search Here"
                                        severity="secondary"
                                        text
                                        icon="pi pi-search"
                                        size="large"
                                        @click="
                                            zoomToSearchResult(
                                                place.resourceid,
                                                'search',
                                            )
                                        "
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div
                        v-else
                        class="resource-details-value"
                        >
                        No associated places available
                    </div>
                </div>
            </div>
    </div>
</template>

<style scoped>
.search-item-details {
    display: flex;
    flex-direction: column;
    padding: 5px;
    border-right: #ddd solid 1px;
    border-left: solid #ddd 1px;
    width: 375px;
    height: 100%;
    background-color: #fff;
}
.title {
    display: flex;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 1.33em;
    font-weight: 500;
    color: #25476a;
    line-height: 1.05;
    margin-bottom: 0px;
    justify-content: space-between;
    border-bottom: #ddd solid 1px;
}

.current-location {
    color: #25476a;
    font-size: 1.25rem;
}

.description {
    font-size: 1.05em;
    color: #25476a;
    margin-bottom: 15px;
    padding: 10px;
    line-height: 1.25;
}

.p-carousel-indicator-list-padding {
    padding: 0px;
}

.carousel-image-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 250px;
}

.carousel-image {
    max-height: 250px;
    max-width: 300px;
}

.resource-details {
    padding: 10px;
}
.value-header {
    color: steelblue;
    font-size: 1.1em;
    font-weight: bold;
}
.value-entry {
    font-size: 1em;
    color: #888;
    padding: 0px 3px;
    line-height: 1.15;
}
.resource-details-value {
    color: #25476a;
    padding: 0px 3px;
}
.zoom-to-item {
    padding: 0 1rem;
    display: flex;
    justify-content: start;
}
.close-button:hover {
    color: #25476a;
}
</style>

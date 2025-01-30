<script setup lang="ts">
import { onMounted, inject, ref, watch } from "vue";
import type { Acquisition } from "@/afrc/Search/types";
import { fetchResourceData, fetchImageData } from "@/afrc/Search/api.ts";
import type { Ref } from "vue";
import Button from "primevue/button";
import Carousel from "primevue/carousel";

const resultSelected = inject("resultSelected") as Ref<string>;
const resultsSelected = inject("resultsSelected") as Ref<string[]>;

const displayname: Ref<string> = ref("");
const displaydescription: Ref<string> = ref("");
const images: Ref<string[]> = ref([]);
const acquisitions: Ref<Acquisition[]> = ref([]);
const identifier: Ref<string> = ref("");

onMounted(async () => {
    getData();
});

watch(resultSelected, () => {
    getData();
});

async function getData() {
    let imageData: string[] = [];
    const resp = await fetchResourceData(resultSelected.value);
    const imageResourceids = resp.resource["Digital Reference"]?.map((tile: { [key: string]: any; }) => tile["Digital Source"]["resourceId"]); // eslint-disable-line @typescript-eslint/no-explicit-any
    const accessionNumber = resp.resource['Identifier']?.find((x: {[key: string]: any;}) => x["Identifier_type"]["@display_value"]==="Accession Number"); // eslint-disable-line @typescript-eslint/no-explicit-any

    acquisitions.value = resp.resource["Addition to Collection"]?.map((x: { [key: string]: any; }) => ( // eslint-disable-line @typescript-eslint/no-explicit-any
        {
            "person": x["Addition to Collection_carried out by"]["@display_value"],
            "date": x["Addition to Collection_time"]["Addition to Collection_time_begin of the begin"]["@display_value"],
            "details": x["Addition to Collection_Statement"]?.map((y: {[key: string]: any;}) => (y["Addition to Collection_Statement_content"]["@display_value"])).join(" ") // eslint-disable-line @typescript-eslint/no-explicit-any
        })); // eslint-disable-line @typescript-eslint/no-explicit-any
    displayname.value = resp.displayname;
    displaydescription.value = resp.displaydescription;
    identifier.value = accessionNumber ? accessionNumber["Identifier_content"]["@display_value"] : "";

    if (imageResourceids) {
        imageData = await fetchImageData(imageResourceids);
        images.value = imageData;
    } else {
        images.value = [];
    }
}

function clearResult() {
    resultSelected.value = "";
    resultsSelected.value = [];
}
</script>

<template>
    <div class="search-item-details">
        <div class="title">
            <div style="display: flex; flex-direction: column; padding: 3px">
                <div>
                    {{ displayname || "No name provided" }}
                </div>
                <div style="font-size: 0.7em; color: steelblue; font-style: italic; font-weight: 400;">
                    {{ identifier }}
                </div>
            </div>
            <div>
                <Button
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
            <div v-if="displaydescription && displaydescription != 'Undefined'">{{ displaydescription }}</div>
            <div v-else>No description provided</div> 
        </div>
        <div v-if="images.length" class="images">
        <Carousel :value="images" :numVisible="2" :numScroll="1" containerClass="flex items-center">
            <template #item="image">
                <div class="border border-surface-200 dark:border-surface-700 rounded m-2  p-4">
                    <div class="mb-4">
                        <div class="relative mx-auto">
                            <div style="padding: 3px">
                            <img :src="image.data" height="120px" width="120px" class="w-full rounded" />
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </Carousel>
        </div>
        <div class="resource-details"  style="color: grey">
            <div class="value-header">Material Information</div>
            <div class="value-entry">Chemical (CAS) Number:<span class="resource-details-value">1309-36-0</span></div>
            <div class="value-entry">Chemical Formula:<span class="resource-details-value">FeS2</span></div>
            <div class="value-entry">Chemical Name:<span class="resource-details-value">Iron Disulfide</span></div>
            <div class="value-entry">Common Name:<span class="resource-details-value">Pyrite, Fool's Gold</span></div>
        </div>
        <div  v-if="acquisitions"  class="resource-details">
            <div class="value-header">Acquisition Information</div>
            <div v-for="(acquisition, index) in acquisitions" :key="index">
                <div class="value-entry">Acquired by:<span class="resource-details-value">{{ acquisition.person }}</span></div>
                <div class="value-entry">Acquired on:<span class="resource-details-value">{{ acquisition.date }}</span></div>
                <div class="value-entry">Acquisition Details:<span class="resource-details-value">{{ acquisition.details }}</span></div>
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
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 5px;
    justify-content: space-between;
    border-bottom: #ddd solid 1px;
}
.description {
    font-size: 1em;
    margin-bottom: 15px;
    padding: 10px;
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
    padding: 0px 3px;
}
.resource-details-value {
    color: steelblue;
    padding: 0px 3px;
}
</style>

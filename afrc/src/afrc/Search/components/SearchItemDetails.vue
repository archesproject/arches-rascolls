<script setup lang="ts">
import { onMounted, inject, ref, watch } from "vue";
import { fetchResourceData, fetchImageData } from "@/afrc/Search/api.ts";
import type { Ref } from "vue";
import Button from "primevue/button";
import Carousel from "primevue/carousel";

const resultSelected = inject("resultSelected") as Ref<string>;
const resultsSelected = inject("resultsSelected") as Ref<string[]>;

let displayname: Ref<string> = ref("");
let displaydescription: Ref<string> = ref("");
let images: Ref<string[]> = ref([]);

onMounted(async () => {
    getData();
});

watch(resultSelected, () => {
    getData();
});

async function getData() {
    let imageData: string[] = [];
    const resp = await fetchResourceData(resultSelected.value);
    const imageResourceids = resp.resource["Digital Reference"]?.map((tile: { [key: string]: any; }) => tile["Digital Source"]["resourceId"]);
    displayname.value = resp.displayname;
    displaydescription.value = resp.displaydescription;
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
                <div
                    style="
                        font-size: 0.7em;
                        color: steelblue;
                        font-style: italic;
                        font-weight: 400;
                    "
                >
                    (Room 32, Row 2, Shelf 3)
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
            {{ displaydescription || "No description provided" }}
            <span
                >Sed ut perspiciatis, unde omnis iste natus error sit voluptatem
                accusantium doloremque laudantium, totam rem aperiam eaque ipsa,
                quae ab illo inventore veritatis et quasi architecto beatae
                vitae dicta sunt, explicabo. Nemo enim ipsam voluptatem, quia
                voluptas sit, aspernatur aut odit aut fugit</span
            >
        </div>
        <div class="images">
            <Carousel
                :value="images"
                :num-visible="2"
                :num-scroll="1"
                container-class="flex items-center"
            >
                <template #item="image">
                    <div
                        class="border border-surface-200 dark:border-surface-700 rounded m-2 p-4"
                    >
                        <div class="mb-4">
                            <div class="relative mx-auto">
                                <div style="padding: 3px">
                                    <img
                                        :src="image.data"
                                        height="120px"
                                        width="120px"
                                        class="w-full rounded"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </Carousel>
        </div>
        <div class="resource-details">
            <div class="value-header">Chemical Information</div>
            <div class="value-entry">
                Chemical (CAS) Number:<span class="resource-details-value"
                    >1309-36-0</span
                >
            </div>
            <div class="value-entry">
                Chemical Formula:<span class="resource-details-value"
                    >FeS2</span
                >
            </div>
            <div class="value-entry">
                Chemical Name:<span class="resource-details-value"
                    >Iron Disulfide</span
                >
            </div>
            <div class="value-entry">
                Common Name:<span class="resource-details-value"
                    >Pyrite, Fool's Gold</span
                >
            </div>
        </div>
        <div class="resource-details">
            <div class="value-header">Aquisition Information</div>
            <div class="value-entry">
                Acquired by:<span class="resource-details-value"
                    >Art Kaplan</span
                >
            </div>
            <div class="value-entry">
                Acquired from:<span class="resource-details-value"
                    >Minerals-R-Us</span
                >
            </div>
            <div class="value-entry">
                Acquired on:<span class="resource-details-value"
                    >Feb 18, 2001</span
                >
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

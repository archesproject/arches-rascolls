<script setup lang="ts">
import { onMounted, inject, ref } from "vue";
import type { Ref } from "vue";

import Button from "primevue/button";

import arches from "arches";
import { fetchImageData } from "@/afrc/Search/api.ts";

const resultsSelected = inject("resultsSelected") as Ref<string[]>;
const resultSelected = inject("resultSelected") as Ref<string>;
const image: Ref<string> = ref("");

onMounted(async () => {
    const res = await fetchImageData([props.searchResult._source.resourceinstanceid], true);
    if (res.length > 0) {
        image.value = res[0];
    }
});

const props = defineProps({
    searchResult: {
        type: Object,
        required: true,
    },
});

function highlightResult(resourceid: string) {
    if (!resultSelected.value) {
        resultsSelected.value = [resourceid];
    }
}

function selectResult(resourceid: string) {
    resultSelected.value = resourceid;
    resultsSelected.value = [resourceid];
}
</script>

<template>
    <section
        class="result"
        :class="{
            hovered: resultsSelected.includes(
                searchResult._source.resourceinstanceid,
            ),
        }"
        @mouseenter="highlightResult(searchResult._source.resourceinstanceid)"
    >
        <div class="image-placeholder">
            <img v-if="image" :src="image" class="image" />
            <div v-else class="no-image">No image available</div>
        </div>
        <div class="result-content">
            <div class="result-displayname">
                {{ props.searchResult._source.displayname }}
            </div>
            <div class="breadcrumb">
                (North and Central America &gt; United States &gt; Missouri &gt;
                Greene)
            </div>
            <div class="scope-note" v-html="searchResult._source.displaydescription"></div>
            <div class="actions">
                <Button
                    label="...show more"
                    severity="secondary"
                    text
                    size="large"
                    @click="
                        selectResult(searchResult._source.resourceinstanceid)
                    "
                />
                <Button
                    label="edit"
                    severity="secondary"
                    text
                    as="a"
                    target="_blank"
                    size="large"
                    icon="pi pi-pen-to-square"
                    :href="arches.urls.resource + '/' + searchResult._id"
                />
            </div>
        </div>
    </section>
</template>

<style scoped>
.result {
    background-color: #fff;
    border: 1px solid #ddd;
    display: flex;
    flex-direction: row;
}
.result.hovered {
    background-color: rgb(239 245 252);
    border: 1px solid rgb(139 145 252);
}
.result .result-content {
    height: 16rem;
    overflow: hidden;
    padding-inline-start: 10px;
    padding: 15px;
}
.result h2 {
    margin: 0 0 10px;
    font-size: 1.2rem;
}
.result .breadcrumb {
    color: #415790;
    font-size: 1.1rem;
    margin-bottom: 10px;
    padding: unset;
}
.result .image-placeholder {
    width: 16rem;
    height: 16rem;
    min-width: 16rem;
    background-color: #eee;
}
.result-displayname {
    font-size: 1.5rem;
    font-weight: bold;
}
.scope-note {
    font-size: 1.2rem;
}
.actions {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}
.no-image { 
    display: flex;
    justify-content: center;
    align-items: center;
    height: 158px;
    width: 160px;
    color: #555;
    background-color: rgb(236, 236, 236);
}
.image {
    height: 158px; 
    width: 160px;
}
</style>

<script setup lang="ts">
import { inject } from "vue";
import type { Ref } from "vue";

import Button from "primevue/button";

import arches from "arches";

const resultsSelected = inject("resultsSelected") as Ref<string[]>;
const resultSelected = inject("resultSelected") as Ref<string>;
const showMap = inject("showMap") as Ref<boolean>;

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
    <section>
        <div class="result">
            <div class="image-placeholder">
                <img src="https://picsum.photos/160" />
            </div>
            <div class="result-content">
                <div>
                    <div class="result-displayname">
                        {{ props.searchResult._source.displayname }}
                    </div>
                    <div class="item-current-location">
                        <span class="breadcrumb-title">Current location:</span>
                        <span class="breadcrumb">CGI Room 222, Aisle 3, Level B, Case 3</span>
                    </div>
                    <div class="scope-note">
                        <span class="scope-note-title">Item description:</span><span class="scope-note-content">{{ searchResult._source.displaydescription }}</span>
                    </div>
                </div>
                <div>
                    <div class="actions">
                        <Button class="action-button"
                            label="show more"
                            severity="secondary"
                            text
                            size="large"
                            @click="
                                selectResult(searchResult._source.resourceinstanceid)
                            "
                        />
                        <Button class="action-button"
                            label="edit"
                            severity="secondary"
                            text
                            as="a"
                            target="_blank"
                            size="large"
                            icon="pi pi-pen-to-square"
                            :href="'./' + arches.urls.resource + '/' + searchResult._id"
                        />
                    </div>
                </div>
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
    border-radius: 3px;
}

.map-sidebar .result {
    border: none;
    border-bottom: 1px solid #ddd;
}

.result:hover {
    background: #f7f6fa;
    border: 1px solid rgb(139 145 252);
}

.map-sidebar .result:hover {
    border: none;
    border-bottom: 1px solid #ddd;
    background: #f7f6fa;
}

.result .result-content {
    overflow: hidden;
    padding-inline-start: 10px;
    padding: 10px 10px 0px 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.map-sidebar .result .result-content {
    justify-content: flex-start;
    padding-left: 25px;
}

.result h2 {
    margin: 0 0 10px;
    font-size: 1.2rem;
}
.item-current-location {
    line-height: 1;
}

.result .breadcrumb-title {
    color: #454545;
    font-size: 1.25rem;
    margin-bottom: 10px;
    padding-right: 5px;
}

.result .breadcrumb {
    color: #25476a;
    font-size: 1.25rem;
    margin-bottom: 10px;
    padding: unset;
}

.result .image-placeholder {
    width: 16rem;
    height: 16rem;
    min-width: 16rem;
    background-color: #eee;
}

.map-sidebar .result .image-placeholder {
    display: none;
}

.result-displayname {
    font-size: 1.33em;
    font-weight: 500;
    color: #25476a;
    margin: 0px;
    line-height: 1.05;
}
.scope-note {
    margin-top: 5px;
    font-size: 1.125em;
}

.scope-note-title {
    color: #777;
    padding-right: 5px;
}

.map-sidebar .result .scope-note-title {
    display: none;
}

.scope-note-content {
    color: #25476a;
}

.map-sidebar .result .scope-note-content {
    font-size: 0.9em;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    padding-bottom: 5px;
}
.p-button-text.p-button-secondary.action-button {
    border-radius: 2px;
}

.p-button-text.p-button-secondary.action-button:hover {
    background: #DFDBEB;
    color: #25476a;
}
</style>

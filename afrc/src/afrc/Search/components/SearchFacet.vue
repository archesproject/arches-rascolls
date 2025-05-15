<script setup lang="ts">
import { inject, ref } from "vue";
import type { Ref } from "vue";

import { useGettext } from "vue3-gettext";

import type { GenericObject, SearchFilter } from "@/afrc/Search/types";
import { FACET_FILTER_TYPE } from "@/afrc/Search/constants.ts";

const { $gettext } = useGettext();
const searchFilters = inject("searchFilters") as Ref<SearchFilter[]>;
const query = inject("query") as GenericObject;
const queryString = inject("queryString") as Ref<string>;

const searchFacetConfig = [
    {
        name: "reference-objects",
        title: $gettext("Reference Objects"),
        description: $gettext(
            "Reference collection items such as papers, paints, textiles",
        ),
        icon: "pi pi-address-book",
        valueid: "f697d7f2-4956-4b14-8910-c7ca673e74ca",
        selected: ref(false),
    },
    {
        name: "samples",
        title: $gettext("Samples"),
        description: $gettext(
            "Materials removed from works of art or other reference objects",
        ),
        icon: "pi pi-chart-line",
        valueid: "acccf634-141a-4710-bfdd-5f6501bea189",
        selected: ref(false),
    },
    {
        name: "building-materials",
        title: $gettext("Building Materials"),
        description: $gettext("Construction materials and related objects"),
        icon: "pi pi-building",
        valueid: "e00d394b-e914-4c89-961d-db8e62410ba2",
        selected: ref(false),
    },
];

function onSelectFacet(facet: GenericObject) {
    const componentName = "advanced-search";
    query[componentName] = [];

    // Toggle the selected state of the facet
    facet.selected.value = !facet.selected.value;

    // Clear all the facet filter chips
    searchFilters.value = searchFilters.value.filter(
        (filter) => filter.type !== FACET_FILTER_TYPE,
    );

    const selectedFacets = searchFacetConfig.filter(
        (facet) => facet.selected.value,
    );

    if (selectedFacets.length > 0) {
        selectedFacets.forEach((facet, index) => {
            if (facet) {
                const valueid = facet.valueid;
                query[componentName].push({
                    op: index === 0 ? "and" : "or",
                    "e9b8d73c-09b7-11f0-b84f-0275dc2ded29": {
                        op: "eq",
                        val: valueid,
                    },
                });
                searchFilters.value.push({
                    id: facet.name,
                    name: facet.title,
                    type: FACET_FILTER_TYPE,
                    clear: () => onSelectFacet(facet),
                });
            }
        });
    } else {
        delete query[componentName];
    }
    queryString.value = JSON.stringify(query);
}
</script>

<template>
    <div>
        <h1 class="section-header">Search Facets</h1>
        <p class="section-tag">
            Select the Collections that you want to include in your search
        </p>
    </div>
    <section class="facets">
        <template
            v-for="facet in searchFacetConfig"
            :key="facet.name"
        >
            <div
                class="facet-item-toggle"
                @click.prevent="onSelectFacet(facet)"
            >
                <div
                    class="facet-item"
                    :class="{ selected: facet.selected.value }"
                >
                    <div
                        class="facet-item-icon pi"
                        :class="facet.icon"
                    ></div>
                    <h2 class="facet-item-title">{{ facet.title }}</h2>
                    <p class="facet-item-tag">
                        {{ facet.description }}
                    </p>
                    <div>
                        {{ facet.selected ? "Unselect" : "Select" }}
                        this facet
                    </div>
                </div>
            </div>
        </template>
    </section>
</template>

<style scoped>
.section-header {
    font-size: 1.33em;
    font-weight: 500;
    color: #25476a;
    margin-top: 0px;
    margin-bottom: 3px;
}

.section-tag {
    font-size: 1em;
    font-weight: 300;
    color: #888;
    line-height: 1.5;
    margin: 0px;
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
    font-size: 1.45rem;
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
    font-size: 1.2rem;
    color: #aaa;
    line-height: 1.15;
    margin: 0px;
}
.facet-item-toggle {
    color: #007bff;
    font-size: 1.15rem;
}
</style>

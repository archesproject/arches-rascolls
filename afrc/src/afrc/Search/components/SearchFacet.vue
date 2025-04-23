<script setup lang="ts">
import { inject } from "vue";
import type { Ref } from "vue";

import { useGettext } from "vue3-gettext";

import type { GenericObject, SearchFilter } from "@/afrc/Search/types";
import { FACET_FILTER_TYPE } from "@/afrc/Search/constants.ts";

const { $gettext } = useGettext();
const searchFilters = inject("searchFilters") as Ref<SearchFilter[]>;
const query = inject("query") as GenericObject;
const queryString = inject("queryString") as Ref<string>;
const selectedFacetName = inject("selectedFacetName") as Ref<string>;

const searchFacetConfig = [
    {
        name: "reference-objects",
        title: $gettext("Reference Objects"),
        description: $gettext(
            "Reference collection items such as papers, paints, textiles",
        ),
        icon: "pi pi-address-book",
        valueid: "f697d7f2-4956-4b14-8910-c7ca673e74ca",
    },
    {
        name: "samples",
        title: $gettext("Samples"),
        description: $gettext(
            "Materials removed from works of art or other reference objects",
        ),
        icon: "pi pi-chart-line",
        valueid: "acccf634-141a-4710-bfdd-5f6501bea189",
    },
    {
        name: "building-materials",
        title: $gettext("Building Materials"),
        description: $gettext("Construction materials and related objects"),
        icon: "pi pi-building",
        valueid: "e00d394b-e914-4c89-961d-db8e62410ba2",
    },
];

function onSelectFacet(facet_name: string) {
    const componentName = "advanced-search";
    selectedFacetName.value =
        selectedFacetName.value === facet_name ? "" : facet_name;

    // Clear all the facet filter chips
    searchFilters.value = searchFilters.value.filter(
        (filter) => filter.type !== FACET_FILTER_TYPE,
    );

    if (selectedFacetName.value !== "") {
        const facet = searchFacetConfig.find(
            (facet) => facet.name === selectedFacetName.value,
        );
        const valueid = facet!.valueid;
        query[componentName] = [
            {
                op: "and",
                "e9b8d73c-09b7-11f0-b84f-0275dc2ded29": {
                    op: "eq",
                    val: valueid,
                },
            },
        ];
        if (
            !searchFilters.value.find((filter) => filter.name === facet!.title)
        ) {
            searchFilters.value.push({
                id: facet!.name,
                name: facet!.title,
                type: FACET_FILTER_TYPE,
                clear: () => onSelectFacet(facet!.name),
            });
        }
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
                @click.prevent="onSelectFacet(facet.name)"
            >
                <div
                    class="facet-item"
                    :class="{ selected: selectedFacetName === facet.name }"
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
                        {{
                            selectedFacetName === facet.name
                                ? "Unselect"
                                : "Select"
                        }}
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

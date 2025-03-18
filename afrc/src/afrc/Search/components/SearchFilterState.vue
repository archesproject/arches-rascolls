<script setup lang="ts">
import Button from "primevue/button";
import { inject } from "vue";
import type { Ref } from "vue";
import type { SearchFilter } from "@/afrc/Search/types.ts";
const searchFilters = inject("searchFilters") as Ref<SearchFilter[]>;
</script>

<template>
    <div class="search-filters">
        <div
            v-for="(filter, index) in searchFilters"
            :key="index"
            class="search-filter"
        >
            <Button
                :label="filter.name"
                class="p-button"
                severity="info"
                raised
                @click="filter.clear()"
            />
        </div>
    </div>
</template>

<style scoped>
.search-filter {
    margin: 0px;
    padding: 3px;
}
.search-filters {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
}
</style>

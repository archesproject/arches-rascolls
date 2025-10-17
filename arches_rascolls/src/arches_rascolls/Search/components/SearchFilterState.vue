<script setup lang="ts">
import Button from "primevue/button";
import { inject } from "vue";
import type { Ref } from "vue";
import type { SearchFilter } from "@/arches_rascolls/Search/types.ts";
const searchFilters = inject("searchFilters") as Ref<SearchFilter[]>;
</script>

<template>
    <div class="search-filters">
        <div
            v-for="(filter, index) in searchFilters"
            :key="index"
            class="search-filter-chip"
        >
            <Button
                :style="{ fontSize: '1.55rem', borderRadius: '3px' }"
                :label="filter.name"
                size="large"
                severity="secondary"
                icon="pi pi-times"
                icon-pos="right"
                @click="filter.clear()"
            />
        </div>
    </div>
</template>

<style scoped>
.search-filter-chip {
    padding: 3px;
}

.search-filters {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
}
</style>

<script setup lang="ts">
import { inject, onMounted, ref, watch } from "vue";

import RadioButton from "primevue/radiobutton";

import type { Map } from "maplibre-gl";
import type { PropType } from "vue";

import type { Basemap } from "@/arches_rascolls/Search/types.ts";

defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
    settings: {
        type: Object as PropType<Record<string, unknown> | null>,
        default: null,
    },
});

const basemaps: Basemap[] = inject("basemaps", []);
const selectedBasemap = ref<Basemap | null>(null);

watch(selectedBasemap, (newBasemap) => {
    basemaps.forEach((basemap) => {
        basemap.active = basemap === newBasemap;
    });
});

onMounted(() => {
    const activeBasemap = basemaps.find((basemap) => basemap.active);
    if (activeBasemap) {
        selectedBasemap.value = activeBasemap;
    }
});
</script>

<template>
    <div
        v-for="basemap in basemaps"
        :key="basemap.id"
    >
        <div class="basemap-item">
            <RadioButton
                v-model="selectedBasemap"
                :value="basemap"
                :label="basemap.name"
            />
            <label>{{ basemap.name }}</label>
        </div>
    </div>
</template>

<style scoped>
.basemap-item {
    display: flex;
    align-items: baseline;
    padding: 10px;
}

.basemap-item label {
    padding: 7px;
}

.basemap-item:hover {
    background: #f7f6fa;
}
</style>

<script setup lang="ts">
import { inject, ref } from "vue";

import ToggleSwitch from "primevue/toggleswitch";

import type { Map } from "maplibre-gl";
import type { PropType, Ref } from "vue";

import type { MapLayer } from "@/afrc/Search/types.ts";

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

const overlays: Ref<Array<MapLayer>> = inject("overlays", ref([]));
</script>

<template>
    <div
        v-for="overlay in overlays"
        :key="overlay.id"
    >
        <div class="overlay-item">
            <ToggleSwitch v-model="overlay.addtomap" />
            <label>{{ overlay.name }}</label>
        </div>
    </div>
</template>

<style scoped>
.overlay-item {
    display: flex;
    align-items: center;
    padding: 10px;
}
.overlay-item label {
    padding: 7px;
    margin-bottom: 0;
}
.overlay-item:hover {
    background: #f7f6fa;
}
</style>

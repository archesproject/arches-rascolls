<script setup lang="ts">
import { ref } from "vue";

import { useGettext } from "vue3-gettext";

import DrawControls from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/DrawControls.vue";
// import FeatureUploader from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/FeatureUploader.vue";
import BufferControls from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/BufferControls.vue";
import Button from 'primevue/button';

import type { Map } from "maplibre-gl";
import type { PropType } from "vue";

const { $gettext } = useGettext();

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


const drawControlsRef = ref<InstanceType<typeof DrawControls> | null>(null);
const bufferControlsRef = ref<InstanceType<typeof BufferControls> | null>(null);

function deleteSelectedFeature() {
    drawControlsRef.value?.deleteSelectedDrawnFeature();
}

function clearAllDrawnFeatures() {
    drawControlsRef.value?.deleteAllDrawnFeatures();
}
</script>

<template>
    <DrawControls
        ref="drawControlsRef"
        :map="map"
    />
    <BufferControls
        ref="bufferControlsRef"
        :map="map"
    />
    <!-- <FeatureUploader :map="map" /> -->

    <div class="clear-btns">
        <Button @click="deleteSelectedFeature" size="large" severity="secondary">
            {{ $gettext("Clear Selected") }}
        </Button>

        <Button @click="clearAllDrawnFeatures" size="large" severity="secondary">
            {{ $gettext("Clear All") }}
        </Button>
    </div>
</template>

<style scoped>
    .clear-btns {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        padding-top: 15px;
    }
</style>
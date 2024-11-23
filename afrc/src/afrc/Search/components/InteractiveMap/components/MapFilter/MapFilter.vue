<script setup lang="ts">
import { ref } from "vue";

import { useGettext } from "vue3-gettext";

import DrawControls from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/DrawControls.vue";
import FeatureUploader from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/FeatureUploader.vue";
import BufferControls from "@/afrc/Search/components/InteractiveMap/components/MapFilter/components/BufferControls.vue";

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
    <BufferControls
        ref="bufferControlsRef"
        :map="map"
    />
    <DrawControls
        ref="drawControlsRef"
        :map="map"
    />
    <FeatureUploader :map="map" />

    <button @click="deleteSelectedFeature">
        {{ $gettext("Delete Selected Feature") }}
    </button>
    <button @click="clearAllDrawnFeatures">
        {{ $gettext("Clear All Features") }}
    </button>
</template>

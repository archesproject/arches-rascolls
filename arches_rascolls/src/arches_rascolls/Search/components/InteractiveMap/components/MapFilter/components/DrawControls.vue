<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { useGettext } from "vue3-gettext";

import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";

import type { Map } from "maplibre-gl";
import type { PropType } from "vue";
import Select from "primevue/select";

import {
    POINT,
    LINE,
    POLYGON,
    DRAW_POINT,
    DRAW_LINE_STRING,
    DRAW_POLYGON,
    DRAW_CREATE_EVENT,
} from "@/arches_rascolls/Search/components/InteractiveMap/constants.ts";

const { $gettext } = useGettext();

const props = defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
});

defineExpose({
    deleteSelectedDrawnFeature,
    deleteAllDrawnFeatures,
});

let draw: typeof MapboxDraw;
const selectedDrawType = ref();

const options = ref([
    { label: $gettext("Draw a Marker"), code: POINT },
    { label: $gettext("Draw a Polyline"), code: LINE },
    { label: $gettext("Draw a Polygon"), code: POLYGON },
]);

watch(
    () => selectedDrawType.value,
    (newDrawType) => {
        if (newDrawType) {
            props.map.getCanvas().style.cursor = "crosshair";
            if (newDrawType === POINT) {
                draw.changeMode(DRAW_POINT);
            } else if (newDrawType === LINE) {
                draw.changeMode(DRAW_LINE_STRING);
            } else if (newDrawType === POLYGON) {
                draw.changeMode(DRAW_POLYGON);
            }
        } else {
            props.map.getCanvas().style.cursor = "";
        }
    },
);

onMounted(() => {
    draw = props.map._controls.find(
        (control) => control instanceof MapboxDraw,
    ) as typeof MapboxDraw;

    props.map.on(DRAW_CREATE_EVENT, updateDropdown);
});

onUnmounted(() => {
    props.map.off(DRAW_CREATE_EVENT, updateDropdown);
});

function updateDropdown() {
    selectedDrawType.value = "";
}

function deleteAllDrawnFeatures() {
    draw.deleteAll();
    props.map.fire("draw.delete");
}

function deleteSelectedDrawnFeature() {
    const selectedFeatures = draw.getSelected();

    if (selectedFeatures.features.length) {
        const featureId = selectedFeatures.features[0].id;
        draw.delete(featureId);
        props.map.fire("draw.delete");
    }
}
</script>

<template>
    <div class="draw-controls">
        <label for="draw-type">Filter type</label>
        <Select
            id="draw-type"
            v-model="selectedDrawType"
            :options="options"
            option-label="label"
            option-value="code"
            placeholder="Draw a"
            class="w-full md:w-56"
            fluid
        />
    </div>
</template>
<style scoped>
.draw-controls {
    align-items: baseline;
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin-top: 15px;
}
</style>

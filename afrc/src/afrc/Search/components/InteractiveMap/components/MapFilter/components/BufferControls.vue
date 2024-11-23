<script setup lang="ts">
import { ref, watch, inject } from "vue";
import { useGettext } from "vue3-gettext";

import MapboxDraw from "@mapbox/mapbox-gl-draw";

import type { Feature, Map } from "maplibre-gl";
import type { PropType, Ref } from "vue";
import {
    DRAW_UPDATE_EVENT,
    METERS,
} from "@/afrc/Search/constants.ts";

const { $gettext } = useGettext();

const props = defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
});

const selectedDrawnFeature = inject("selectedDrawnFeature", ref(null));

const bufferDistance: Ref<number | ""> = ref(0);
const selectedUnits: Ref<string> = ref(METERS);

watch([bufferDistance, selectedUnits], () => {
    if (bufferDistance.value === "" || bufferDistance.value < 0) {
        bufferDistance.value = 0;
    }

    if (selectedDrawnFeature.value) {
        let draw = props.map._controls.find(
            (control) => control instanceof MapboxDraw,
        ) as typeof MapboxDraw;

        (selectedDrawnFeature.value as Feature).properties.buffer_distance =
            bufferDistance.value;
        (selectedDrawnFeature.value as Feature).properties.buffer_units =
            selectedUnits.value;

        draw.add(selectedDrawnFeature.value);
        props.map.fire(DRAW_UPDATE_EVENT, {
            features: [selectedDrawnFeature.value],
        });
    }
});

watch(
    selectedDrawnFeature,
    (feature: Feature | null) => {
        if (feature) {
            if (
                Number.isInteger(feature.properties.buffer_distance) &&
                feature.properties.buffer_units
            ) {
                bufferDistance.value = feature.properties.buffer_distance;
                selectedUnits.value = feature.properties.buffer_units;

                return;
            }
        }

        bufferDistance.value = 0;
        selectedUnits.value = METERS;
    },
    { immediate: true },
);
</script>

<template>
    <div>
        <label for="bufferDistance">{{ $gettext("Buffer Distance:") }}</label>
        <input
            id="bufferDistance"
            v-model.number="bufferDistance"
            type="number"
            min="0"
            step="1"
        />

        <label for="unit">{{ $gettext("Unit:") }}</label>
        <select
            id="unit"
            v-model="selectedUnits"
        >
            <option value="meters">{{ $gettext("Meters") }}</option>
            <option value="feet">{{ $gettext("Feet") }}</option>
            <option value="miles">{{ $gettext("Miles") }}</option>
            <option value="kilometers">{{ $gettext("Kilometers") }}</option>
        </select>
    </div>
</template>

<style scoped>
label {
    margin-right: 10px;
}

input {
    padding: 5px;
    width: 100px;
}
</style>

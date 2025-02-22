<script setup lang="ts">
import { ref, watch, inject } from "vue";
import { useGettext } from "vue3-gettext";

import MapboxDraw from "@mapbox/mapbox-gl-draw";

import type { Feature, Map } from "maplibre-gl";
import type { PropType, Ref } from "vue";
import Select from 'primevue/select';
import InputNumber from 'primevue/inputnumber';
import { 
    DRAW_UPDATE_EVENT, 
    METERS, 
    FEET, 
    MILES, 
    KILOMETERS,
    YARDS
} from "@/afrc/Search/components/InteractiveMap/constants.ts";
import Panel from 'primevue/panel';
import type { GenericObject } from "@/afrc/Search/types.ts";

const { $gettext } = useGettext();

const props = defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
});

const selectedDrawnFeature = inject("selectedDrawnFeature", ref(null));

const bufferDistance: Ref<number | 0> = ref(0);
    
const options = ref([
    { label: $gettext("meters"), code: METERS },
    { label: $gettext("feet"), code: FEET },
    { label: $gettext("miles"), code: MILES },
    { label: $gettext("kilometers"), code: KILOMETERS },
    { label: $gettext("yards"), code: YARDS },
]);

const selectedUnits: Ref<string> = ref(options.value[0].code);

watch([bufferDistance, selectedUnits], () => {
    if (bufferDistance.value < 0) {
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
    <Panel :pt="{title: { style: { 'font-weight': 500 }}}" header="Buffer Selected Feature" style="margin-top: 12px">
        <div class="buffer-controls">
            <label for="buffDistance">Distance</label>
            <InputNumber 
                v-model="bufferDistance"
                :min="0"
                id="buffDistance"
                :inputStyle="{ fontSize: '1.4rem' }" 
                fluid @input="(e: GenericObject) => bufferDistance = e.value" 
                />
            <Select 
                v-model="selectedUnits" 
                :options="options" 
                id="unit" 
                optionValue="code" 
                placeholder="Units" 
                optionLabel="label" 
                fluid 
            />
        </div>
    </Panel>
</template>

<style scoped>
.buffer-controls {
    align-items: baseline;
    display: flex;
    flex-direction: row;
    gap: 1rem;
}
</style>

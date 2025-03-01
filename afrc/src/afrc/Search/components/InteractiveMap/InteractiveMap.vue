<script setup lang="ts">
import { onMounted, provide, ref, watch } from "vue";

import { useGettext } from "vue3-gettext";
import { useToast } from "primevue/usetoast";

import MapComponent from "@/afrc/Search/components/InteractiveMap/components/MapComponent.vue";
import MapFilter from "@/afrc/Search/components/InteractiveMap/components/MapFilter/MapFilter.vue";
import InteractionsDrawer from "@/afrc/Search/components/InteractiveMap/components/InteractionsDrawer.vue";
// import OverlayControls from "@/afrc/Search/components/InteractiveMap/components/OverlayControls.vue";
// import BasemapControls from "@/afrc/Search/components/InteractiveMap/components/BasemapControls.vue";

import { fetchSettings } from "@/afrc/Search/api.ts";

import { DEFAULT_ERROR_TOAST_LIFE, ERROR } from "@/afrc/Search/constants.ts";

import type { Ref } from "vue";
import type { Feature, Map } from "maplibre-gl";

import type {
    Basemap,
    MapInteractionItem,
    MapLayer,
    MapSource,
    Settings,
} from "@/afrc/Search/types.ts";

const toast = useToast();
const { $gettext } = useGettext();

const props = defineProps<{
    overlays: MapLayer[];
    basemaps: Basemap[];
    sources: MapSource[];
    includeDrawer: boolean;
    popupEnabled: boolean;
    query: string;
}>();

const map: Ref<Map | null> = ref(null);
const settings: Ref<Settings | null> = ref(null);

const mapInteractionItems: MapInteractionItem[] = [
    {
        name: "Filter",
        header: "Map Filter",
        component: MapFilter,
        icon: "pi pi-filter",
    },
    {
        name: "Basemap",
        header: "Map Filter",
        component: MapFilter,
        icon: "pi pi-map",
    },
    {
        name: "Overlays",
        header: "Map Filter",
        component: MapFilter,
        icon: "pi pi-globe",
    },
];

const basemap: Ref<Basemap | null> = ref(null);

const selectedDrawnFeature: Ref<Feature | null> = ref(null);

const emits = defineEmits(["drawnFeatureSelected", "drawnFeaturesUpdated"]);

provide("overlays", props.overlays);
provide("basemaps", props.basemaps);
provide("selectedDrawnFeature", selectedDrawnFeature);
provide("query", props.query);

watch(
    () => props.basemaps,
    (updatedBasemaps) => {
        for (let updatedBasemap of updatedBasemaps) {
            if (updatedBasemap.active) {
                basemap.value = updatedBasemap;
                break;
            }
        }
    },
    { deep: true, immediate: true },
);

onMounted(async () => {
    await fetchSystemSettings();
});

async function fetchSystemSettings() {
    try {
        settings.value = await fetchSettings();
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to fetch settings."),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
}

function updateSelectedDrawnFeature(feature: Feature) {
    selectedDrawnFeature.value = feature;
    emits("drawnFeatureSelected", feature);
}
</script>

<template>
    <div
        v-if="settings"
        style="display: flex; height: 100%; width: 100%"
    >
        <MapComponent
            :settings="settings"
            :basemap="basemap"
            :overlays="overlays"
            :sources="sources"
            :query="query"
            :is-drawing-enabled="true"
            :is-popup-enabled="popupEnabled"
            @map-initialized="
                (mapInstance) => {
                    map = mapInstance;
                }
            "
            @drawn-features-updated="
                (features) => {
                    emits('drawnFeaturesUpdated', features);
                }
            "
            @drawn-feature-selected="updateSelectedDrawnFeature"
        />
        <InteractionsDrawer
            v-if="map && includeDrawer"
            :map="map"
            :settings="settings"
            :items="mapInteractionItems"
        />
    </div>
</template>

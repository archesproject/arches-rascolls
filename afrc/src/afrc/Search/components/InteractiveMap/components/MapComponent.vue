<script setup lang="ts">
import { onMounted, ref, useTemplateRef, watch, inject } from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import maplibregl from "maplibre-gl";
import geojsonExtent from "@mapbox/geojson-extent";

import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import "maplibre-gl/dist/maplibre-gl.css";

import PopupContainer from "@/afrc/Search/components/InteractiveMap/components/PopupContainer/PopupContainer.vue";

import {
    fetchDrawnFeaturesBuffer,
    fetchGeoJSONBounds,
} from "@/afrc/Search/api.ts";

import {
    ACTIVE_LANGUAGE_DIRECTION,
    CLICK_EVENT,
    BUFFER_LAYER_ID,
    BUFFER_FILL_COLOR,
    BUFFER_FILL_OPACITY,
    DIRECT_SELECT,
    DRAW_CREATE_EVENT,
    DRAW_DELETE_EVENT,
    DRAW_SELECTION_CHANGE_EVENT,
    DRAW_UPDATE_EVENT,
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    IDLE,
    LTR,
    METERS,
    SIMPLE_SELECT,
    STYLE_LOAD_EVENT,
    TOP_LEFT,
    TOP_RIGHT,
} from "@/afrc/Search/components/InteractiveMap/constants.ts";

import type { Ref } from "vue";

import type { Feature, FeatureCollection } from "geojson";
import type {
    AddLayerObject,
    Map,
    MapMouseEvent,
    GeoJSONSource,
    ControlPosition,
    Popup,
    SourceSpecification,
} from "maplibre-gl";

import type {
    Basemap,
    Buffer,
    DrawEvent,
    LayerDefinition,
    MapLayer,
    MapSource,
    Settings,
} from "@/afrc/Search/types.ts";

interface Props {
    settings: Settings | null;
    basemap: Basemap | null;
    overlays: MapLayer[];
    sources: MapSource[];
    isDrawingEnabled?: boolean;
    drawnFeatures?: Feature[];
    drawnFeaturesBuffer?: Buffer;
    isPopupEnabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    settings: null,
    basemap: null,
    overlays: () => [],
    sources: () => [],
    isDrawingEnabled: true,
    drawnFeatures: () => [],
    drawnFeaturesBuffer: undefined,
    isPopupEnabled: false,
});

const {
    settings,
    basemap,
    overlays,
    sources,
    isDrawingEnabled,
    drawnFeatures,
    drawnFeaturesBuffer,
    isPopupEnabled,
} = props;

let resultsSelected = inject("resultsSelected") as Ref<string[]>;
let resultSelected = inject("resultSelected") as Ref<string>;

const emits = defineEmits([
    "mapInitialized",
    "drawnFeatureSelected",
    "drawnFeaturesUpdated",
]);

let draw: typeof MapboxDraw;
const map: Ref<Map | null> = ref(null);
const mapContainer = useTemplateRef("mapContainer");
const popupContainer = useTemplateRef("popupContainer");
const resourceOverlaysClickHandlers: {
    [key: string]: (e: MapMouseEvent) => void;
} = {};

const popupInstance: Ref<Popup | null> = ref(null);
const clickedFeatures: Ref<Feature[]> = ref([]);
const clickedCoordinates: Ref<[number, number]> = ref([0, 0]);
const popupContainerRerenderKey = ref(0);

watch(
    () => basemap,
    (basemap) => {
        if (basemap) {
            updateBasemap(basemap as Basemap);
        }
    },
);

watch(
    () => overlays,
    (overlays) => {
        updateMapOverlays(overlays as MapLayer[]);
    },
    { deep: true },
);

watch(
    () => resultsSelected,
    (selected) => {
        if (selected) {
            updateFeatureSelection(selected as Ref<string[]>);
        }
    },
    { deep: true },
);

watch(
    () => drawnFeaturesBuffer,
    () => {
        updateDrawnFeatures();
    },
);

if (isPopupEnabled) {
    watch(clickedFeatures, () => {
        if (popupInstance.value) {
            popupInstance.value.remove();
        }
        popupInstance.value = new maplibregl.Popup()
            .setLngLat(clickedCoordinates.value)
            .setDOMContent(popupContainer.value!.$el)
            .addTo(map.value!);
    });
}

onMounted(() => {
    createMap();
    if (basemap) {
        updateBasemap(basemap as Basemap);
    }
    addMapControls();

    if (settings) {
        map.value!.fitBounds(geojsonExtent(settings.DEFAULT_BOUNDS));
    }

    map.value!.once(STYLE_LOAD_EVENT, () => {
        if (isDrawingEnabled || drawnFeatures) {
            addDrawControls();
        }
        if (drawnFeaturesBuffer?.distance && drawnFeaturesBuffer?.units) {
            addBufferLayer();
        }
        // if (overlays) {
        //     updateMapOverlays(overlays);
        // }
    });
});

async function bufferFeatures(features: FeatureCollection) {
    const featuresToBuffer = {
        ...features,
        features: features.features.filter(
            (feature: Feature) => feature.properties!.buffer_distance,
        ),
    };

    const bufferedFeatures = await fetchDrawnFeaturesBuffer(featuresToBuffer);
    const source = map.value!.getSource(BUFFER_LAYER_ID) as GeoJSONSource;
    source.setData(bufferedFeatures);

    return bufferedFeatures;
}

async function fitBoundsOfFeatures(features: FeatureCollection) {
    const bounds = await fetchGeoJSONBounds(features);

    map.value!.fitBounds(bounds, {
        padding: { top: 50, right: 100, bottom: 50, left: 50 },
    });
}

function updateFeatureSelection(selected: Ref<string[]>) {
    const layers: Array<string> = [];
    overlays.forEach((overlay) => {
        layers.push(
            ...overlay.layerdefinitions.map(
                (layerDefinition) => layerDefinition.id,
            ),
        );
    });
    const features = map.value!.queryRenderedFeatures({ layers: layers });
    features.forEach((feature) => {
        const featureSelected = selected.value.includes(
            feature.properties?.resourceinstanceid,
        );
        map.value!.setFeatureState(
            {
                source: "referencecollections",
                sourceLayer: "referencecollections",
                id: feature.id,
            },
            { selected: featureSelected },
        );
    });
}

function addBufferLayer() {
    map.value!.addSource(BUFFER_LAYER_ID, {
        type: "geojson",
        data: {
            type: "FeatureCollection",
            features: [],
        },
    });

    map.value!.addLayer({
        id: BUFFER_LAYER_ID,
        type: "fill",
        source: BUFFER_LAYER_ID,
        layout: {},
        paint: {
            "fill-color": BUFFER_FILL_COLOR,
            "fill-opacity": BUFFER_FILL_OPACITY,
        },
    });
}

function selectNewlyDrawnFeature(e: DrawEvent) {
    const feature = e.features[0];
    const featureId = feature.id as string;

    map.value!.once(IDLE, () => {
        if (feature.geometry.type === GEOMETRY_TYPE_POINT) {
            draw.changeMode(SIMPLE_SELECT, { featureIds: [featureId] });
        } else if (
            feature.geometry.type === GEOMETRY_TYPE_LINESTRING ||
            feature.geometry.type === GEOMETRY_TYPE_POLYGON
        ) {
            draw.changeMode(DIRECT_SELECT, { featureId });
        }
    });
}

async function updateDrawnFeatures() {
    const drawnFeatures = draw.getAll();

    for (let feature of drawnFeatures.features) {
        if (!feature.properties.buffer_distance) {
            feature.properties.buffer_distance = 0;
        }
        if (!feature.properties.buffer_units) {
            feature.properties.buffer_units = METERS;
        }
    }

    const bufferedFeatures = await bufferFeatures(drawnFeatures);

    emits("drawnFeaturesUpdated", [
        ...drawnFeatures.features,
        ...bufferedFeatures.features,
    ]);

    if (drawnFeatures.features.length) {
        fitBoundsOfFeatures({
            type: "FeatureCollection",
            features: [...drawnFeatures.features, ...bufferedFeatures.features],
        });
    }
}

function createMap() {
    map.value = new maplibregl.Map({
        container: mapContainer.value!,
        zoom: 10,
        center: [-122.105, 37.027],
    });

    emits("mapInitialized", map.value);
}

function updateBasemap(basemap: Basemap) {
    map.value!.setStyle(basemap.url);

    map.value!.once(IDLE, () => {
        updateMapOverlays(overlays);
        addBufferLayer();
        bufferFeatures(draw.getAll());
    });
}

function addMapControls() {
    let mapControlsPosition: ControlPosition;

    if (settings) {
        if (settings[ACTIVE_LANGUAGE_DIRECTION] === LTR) {
            mapControlsPosition = TOP_LEFT;
        } else {
            mapControlsPosition = TOP_RIGHT;
        }

        map.value!.addControl(
            new maplibregl.NavigationControl(),
            mapControlsPosition,
        );
        map.value!.addControl(
            new maplibregl.FullscreenControl(),
            mapControlsPosition,
        );
    }
}

function addDrawControls() {
    draw = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
            point: false,
            line_string: false,
            polygon: false,
            trash: false,
        },
    });

    map.value!.addControl(draw);

    map.value!.on(DRAW_CREATE_EVENT, selectNewlyDrawnFeature);

    map.value!.on(DRAW_CREATE_EVENT, updateDrawnFeatures);
    map.value!.on(DRAW_UPDATE_EVENT, updateDrawnFeatures);
    map.value!.on(DRAW_DELETE_EVENT, updateDrawnFeatures);

    map.value!.on(DRAW_UPDATE_EVENT, (e) => {
        emits("drawnFeatureSelected", e.features[0]);
    });
    map.value!.on(DRAW_SELECTION_CHANGE_EVENT, (e) => {
        emits("drawnFeatureSelected", e.features[0] || null);
    });
    map.value!.on(DRAW_DELETE_EVENT, () => {
        emits("drawnFeatureSelected", null);
    });
}

function addOverlayToMap(overlay: MapLayer) {
    overlay.layerdefinitions.forEach((layerDefinition: LayerDefinition) => {
        map.value!.on("mouseenter", layerDefinition.id, () => {
            map.value!.getCanvas().style.cursor = "pointer";
        });

        map.value!.on("mouseleave", layerDefinition.id, () => {
            map.value!.getCanvas().style.cursor = "";
        });

        if (!map.value!.getSource(layerDefinition.source!)) {
            const source = sources.find(
                (source) => source.name === layerDefinition.source,
            );

            if (source) {
                map.value!.addSource(
                    layerDefinition.source!,
                    source.source as SourceSpecification,
                );
            }
        }
        if (!map.value!.getLayer(layerDefinition.id)) {
            map.value!.addLayer(layerDefinition as AddLayerObject);
        }
    });

    if (overlay.maplayerid && resultsSelected) {
        resourceOverlaysClickHandlers[overlay.maplayerid] = function (
            e: MapMouseEvent,
        ) {
            const features = map.value!.queryRenderedFeatures(e.point, {
                layers: overlay.layerdefinitions.map(
                    (layerDefinition) => layerDefinition.id,
                ),
            });
            if (features.length) {
                popupContainerRerenderKey.value += 1;
                clickedCoordinates.value = [e.lngLat.lng, e.lngLat.lat];
                clickedFeatures.value = features;
                resultsSelected.value = [];
                resultSelected.value = "";
                const uniqueResourceIds = new Set(
                    features.map(
                        (feature) =>
                            feature.properties?.resourceinstanceid as string,
                    ),
                );
                resultsSelected.value = Array.from(uniqueResourceIds);
                resultSelected.value = resultsSelected.value[0];
            } else {
                resultsSelected.value = [];
                resultSelected.value = "";
            }
        };

        map.value!.on(
            CLICK_EVENT,
            resourceOverlaysClickHandlers[overlay.maplayerid],
        );
    }
}

function removeOverlayFromMap(overlay: MapLayer) {
    const sourcesToRemove: { [key: string]: boolean } = {};

    overlay.layerdefinitions.forEach((layerDefinition: LayerDefinition) => {
        if (map.value!.getLayer(layerDefinition.id)) {
            map.value!.removeLayer(layerDefinition.id);

            sourcesToRemove[layerDefinition.source!] = true;
        }
    });

    // verify if any remaining layers are still using the sources
    map.value!.getStyle()?.layers.forEach((layer: LayerDefinition) => {
        if (layer.source && sourcesToRemove[layer.source as string]) {
            delete sourcesToRemove[layer.source as string];
        }
    });

    for (let source of Object.keys(sourcesToRemove)) {
        if (map.value!.getSource(source)) {
            map.value!.removeSource(source);
        }
    }

    if (overlay.maplayerid) {
        if (resourceOverlaysClickHandlers[overlay.maplayerid]) {
            map.value!.off(
                CLICK_EVENT,
                resourceOverlaysClickHandlers[overlay.maplayerid],
            );
            delete resourceOverlaysClickHandlers[overlay.maplayerid];
        }
    }
}

function updateMapOverlays(overlays: Array<MapLayer>) {
    for (let overlay of overlays) {
        if (overlay.addtomap) {
            addOverlayToMap(overlay);
        } else {
            removeOverlayFromMap(overlay);
        }
    }
}
</script>

<template>
    <div
        ref="mapContainer"
        class="map"
    >
        <PopupContainer
            ref="popupContainer"
            :key="popupContainerRerenderKey"
            :features="clickedFeatures"
        />
    </div>
</template>

<style scoped>
.map {
    height: 100%;
    width: 100%;
}
</style>

<style>
.maplibregl-popup-close-button {
    color: black;
    font-size: 1.5rem;
}

.maplibregl-popup-content {
    color: black;
    padding: 0;
    padding-top: 2rem;
    width: 20rem;
    height: 20rem;
}

.map .mapboxgl-ctrl {
    margin: 10px;
}
</style>

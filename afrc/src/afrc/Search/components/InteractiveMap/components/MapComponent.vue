<script setup lang="ts">
import { onMounted, ref, useTemplateRef, watch, inject } from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import maplibregl from "maplibre-gl";
import geojsonExtent from "@mapbox/geojson-extent";
import { selectedLayerDefinition } from "./MapFilter/selected-feature.ts";

import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import "maplibre-gl/dist/maplibre-gl.css";

import PopupContainer from "@/afrc/Search/components/InteractiveMap/components/PopupContainer/PopupContainer.vue";

import {
    fetchDrawnFeaturesBuffer,
    fetchGeoJSONBounds,
    fetchResourceBounds,
    fetchResourceGeoJSON,
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
    MARKER_COLOR,
    MARKER_HIGHLIGHT_COLOR,
    METERS,
    SIMPLE_SELECT,
    STYLE_LOAD_EVENT,
    TOP_LEFT,
    TOP_RIGHT,
    MAP_FILTER_NAME,
    MAP_FILTER_TYPE,
} from "@/afrc/Search/components/InteractiveMap/constants.ts";

import type { Ref } from "vue";

import type { Feature, FeatureCollection } from "geojson";
import {
    type LayerSpecification,
    type AddLayerObject,
    type Map,
    type MapMouseEvent,
    type GeoJSONSource,
    type ControlPosition,
    type Popup,
    type SourceSpecification,
    type VectorTileSource,
} from "maplibre-gl";

import type {
    Basemap,
    Buffer,
    DrawEvent,
    GenericObject,
    LayerDefinition,
    MapLayer,
    MapSource,
    Settings,
    SearchFilter,
} from "@/afrc/Search/types.ts";

interface Props {
    settings: Settings | null;
    basemap: Basemap | null;
    overlays: MapLayer[];
    query: GenericObject[];
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
    query: () => [],
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
let zoomFeature = inject("zoomFeature") as GenericObject;
let highlightResult = inject("highlightResult") as Ref<string>;
const searchFilters = inject("searchFilters") as Ref<SearchFilter[]>;

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
const searchMarkers: GenericObject = {};

watch(
    () => props.basemap,
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
    () => highlightResult,
    () => {
        if (searchMarkers[highlightResult.value]) {
            const marker = searchMarkers[highlightResult.value].marker;
            if (marker._color === MARKER_COLOR) {
                searchMarkers[highlightResult.value].marker = replaceMarker(
                    marker,
                    MARKER_HIGHLIGHT_COLOR,
                );
            } else {
                searchMarkers[highlightResult.value].marker = replaceMarker(
                    marker,
                    MARKER_COLOR,
                );
            }
        } else {
            for (const id in searchMarkers) {
                const marker = searchMarkers[id].marker;
                if (
                    searchMarkers[id].marker._color === MARKER_HIGHLIGHT_COLOR
                ) {
                    searchMarkers[id].marker = replaceMarker(
                        marker,
                        MARKER_COLOR,
                    );
                }
            }
        }
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
    () => props.query,
    () => {
        if (map.value) {
            const src = map.value.getSource(
                "rascolls-search",
            ) as VectorTileSource;
            const oldUrl = src.tiles[0];
            const newUrl = `${oldUrl.split("?cacheclear")[0]}?cacheclear=${Date.now()}`;
            src.setTiles([newUrl]);
            updateCurrentPageOfSearchResults();
        }
    },
    { deep: true, immediate: true },
);

watch(
    () => zoomFeature,
    async (zoomFeature) => {
        if (!zoomFeature.value.resourceid) {
            return;
        }
        const resourceId = zoomFeature.value.resourceid;
        const action = zoomFeature.value.action;
        if (action === "zoom-and-select") {
            resultSelected.value = resourceId;
            resultsSelected.value = [resourceId];
        }
        if (action === "zoom" || action === "zoom-and-select") {
            const extent = await fetchResourceBounds(resourceId as string);
            if (extent) {
                map.value!.fitBounds(
                    [
                        [extent[0], extent[1]],
                        [extent[2], extent[3]],
                    ],
                    { duration: 4500, maxZoom: 12 },
                );
            }
        }
        if (action === "search") {
            const features = await fetchResourceGeoJSON(resourceId as string);
            if (features) {
                draw.deleteAll();
                features.features.forEach((feature: Feature) => {
                    draw.add(feature);
                });
            }
            updateDrawnFeatures();
        }
        zoomFeature.value = { resource: "", action: "" };
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
        map.value!.addSource("selected-resource", {
            type: "geojson",
            data: {
                type: "FeatureCollection",
                features: [],
            },
        });

        selectedLayerDefinition.forEach((layer) => {
            map.value!.addLayer(layer as LayerSpecification);
        });
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

async function updateFeatureSelection(selected: Ref<string[]>) {
    const source = map.value!.getSource("selected-resource") as GeoJSONSource;
    if (source) {
        if (selected.value.length) {
            const geojson = await fetchResourceGeoJSON(selected.value[0]);
            source.setData(geojson);
        } else {
            source.setData({
                type: "FeatureCollection",
                features: [],
            });
        }
    }
}

function createMarker(coordinates: [number, number], color: string) {
    return new maplibregl.Marker({
        color: color,
        draggable: false,
        scale: 0.75,
    })
        .setLngLat(coordinates)
        .addTo(map.value!);
}

function replaceMarker(marker: maplibregl.Marker, color: string) {
    marker.remove();
    const lngLat = marker.getLngLat();
    const coordinates = [lngLat.lng, lngLat.lat] as [number, number];
    return createMarker(coordinates, color);
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

function updateCurrentPageOfSearchResults() {
    for (const id in searchMarkers) {
        searchMarkers[id].marker.remove();
    }
    if (props.query.values!) {
        props.query.forEach(async (searchResult: GenericObject) => {
            if (searchResult._source?.points?.length) {
                const point = searchResult._source.points[0].point;
                const coordinates = [point.lon, point.lat] as [number, number];
                const marker = createMarker(coordinates, MARKER_COLOR);
                searchMarkers[searchResult._id] = {
                    marker: marker,
                    highlighted: false,
                };
            }
        });
    }
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

function clear() {
    draw.deleteAll();
    map.value!.fire("draw.delete");
    searchFilters.value = searchFilters.value.filter(
        (filter) => filter.type !== MAP_FILTER_TYPE,
    );
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
        if (
            !searchFilters.value.find(
                (filter) => filter.name === MAP_FILTER_NAME,
            )
        ) {
            searchFilters.value.push({
                id: MAP_FILTER_NAME,
                name: MAP_FILTER_NAME,
                type: MAP_FILTER_TYPE,
                clear: () => clear(),
            });
        }
    } else {
        searchFilters.value = searchFilters.value.filter(
            (filter) => filter.name !== MAP_FILTER_NAME,
        );
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
        updateCurrentPageOfSearchResults(); // adds markers to the map on initial load
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
        overlay.layerdefinitions.forEach((layerDefinition: LayerDefinition) => {
            if (map.value!.getLayer(layerDefinition.id)) {
                map.value!.removeLayer(layerDefinition.id);
            }
        });
    }
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

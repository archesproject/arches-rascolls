// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type GenericObject = { [key: string]: any };
export type UnspecifiedObject = { [key: string]: UnspecifiedObject | unknown };
import type { Component, Ref } from "vue";
import type { Feature, FeatureCollection, Geometry, GeoJSON } from "geojson";
import type { FilterSpecification } from "maplibre-gl";

export interface MapInteractionItem {
    name: string;
    header: string;
    component: Component;
    icon: string;
}

export interface DrawEvent {
    features: Feature<Geometry>[];
}

export interface Basemap {
    id: string;
    name: string;
    value: string;
    active: boolean;
    url: string;
}
export interface MapLayer {
    activated?: boolean;
    addtomap: boolean;
    centerx?: number | null;
    centery?: number | null;
    icon: string;
    id: number;
    isoverlay: boolean;
    ispublic?: boolean;
    layer_json?: string;
    layerdefinitions: LayerDefinition[];
    legend?: string | null;
    maplayerid?: string;
    name: string;
    title: string;
    url: string;
    searchonly?: boolean;
    sortorder?: number;
    visible: boolean;
    zoom?: number | null;
    nodeid?: string;
}

export interface LayerDefinition {
    id: string;
    type: string;
    source?: string;
    "source-layer"?: string;
    layout?: Record<string, unknown>;
    paint?: Record<string, unknown>;
    filter?: FilterSpecification;
    minzoom?: number;
    maxzoom?: number;
}

export interface MapSource {
    id: number;
    name: string;
    source: {
        type: string;
        url: string;
        data?: GeoJSON;
        tileSize?: number;
        coordinates?: [number, number];
    };
    source_json: string;
}

export interface Settings {
    ACTIVE_LANGUAGE: string;
    ACTIVE_LANGUAGE_DIRECTION: string;
    ARCGIS_TOKEN: string;
    DEFAULT_BOUNDS: GeoJSON;
}

export interface WithinGeometryAndBufferRequestData {
    drawnFeatures: FeatureCollection;
    bufferedFeatures: FeatureCollection;
}

export interface BufferRequestData {
    features: FeatureCollection;
    distance: number;
    units: string;
}

export interface Buffer {
    distance: number;
    units: string;
}

export interface User {
    first_name: string;
    last_name: string;
    username: string;
}

export interface UserRefAndSetter {
    user: Ref<User | null>;
    setUser: (userToSet: User | null) => void;
}

export interface Acquisition {
    person: string;
    date: number;
    details: string;
}

export interface SearchFilter {
    id: string;
    name: string;
    type: string;
    clear(): void;
}

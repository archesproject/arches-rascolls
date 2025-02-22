<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { useGettext } from "vue3-gettext";
import MapboxDraw from "@mapbox/mapbox-gl-draw";

import FileUpload from "primevue/fileupload";
import { useToast } from "primevue/usetoast";

import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
} from "@/afrc/Search/constants.ts";

import {
    DRAW_CREATE_EVENT,
} from "@/afrc/Search/components/InteractiveMap/constants.ts";

import type { Feature } from "geojson";
import type { Map } from "maplibre-gl";
import type {
    FileUploadBeforeSendEvent,
    FileUploadErrorEvent,
    FileUploadUploadEvent,
} from "primevue/fileupload";

const { $gettext } = useGettext();
const toast = useToast();

const props = defineProps<{ map: Map }>();

function addHeader(event: FileUploadBeforeSendEvent) {
    const token = Cookies.get("csrftoken");
    if (token) {
        event.xhr.setRequestHeader("X-CSRFToken", token);
    }
}

function upload(event: FileUploadUploadEvent) {
    if (event.xhr.status !== 200) {
        showError(event);
        return;
    }
    const featureCollection = JSON.parse(event.xhr.responseText);
    const draw = props.map._controls.find(
        (control) => (control as typeof MapboxDraw).add,
    )! as typeof MapboxDraw;
    featureCollection.features.forEach((feat: Feature) => {
        feat.id = draw.add(feat)[0];
    });
    props.map.fire(DRAW_CREATE_EVENT, featureCollection);
}

function showError(event?: FileUploadErrorEvent | FileUploadUploadEvent) {
    toast.add({
        severity: ERROR,
        life: DEFAULT_ERROR_TOAST_LIFE,
        summary: event?.xhr?.statusText || $gettext("Boundary upload failed"),
        detail: JSON.parse(event?.xhr?.responseText ?? "{}").message,
    });
}
</script>

<template>
    <FileUpload
        accept="application/geo+json"
        :url="arches.urls['api-geojson-parse']"
        :auto="true"
        :max-file-size="5e6"
        :with-credentials="true"
        :show-cancel-button="false"
        :show-upload-button="false"
        choose-icon="pi pi-plus-circle"
        :choose-label="$gettext('Upload features')"
        name="geojson"
        @before-send="addHeader($event)"
        @upload="upload($event)"
        @error="showError($event)"
    >
        <template #content>
            <span>{{ $gettext("Formats: GeoJSON") }}</span>
        </template>
    </FileUpload>
</template>

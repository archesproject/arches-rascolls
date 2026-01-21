<script setup lang="ts">
import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

const { $gettext } = useGettext();

enum ExportFormat {
    JSON = "json",
    JSON_LD = "json-ld",
    CSV = "csv",
}

const { exportFormats, resourceInstanceId } = defineProps<{
    exportFormats: string[];
    resourceInstanceId: string;
}>();

function exportData(exportFormat: ExportFormat) {
    let params;
    switch (exportFormat) {
        case ExportFormat.JSON_LD:
            window.open(
                arches.urls.api_resources(resourceInstanceId) +
                    "?format=json-ld",
                "_blank",
            );
            break;
        case ExportFormat.JSON:
            window.open(
                arches.urls.api_resources(resourceInstanceId) +
                    "?format=json&v=beta",
                "_blank",
            );
            break;
        case ExportFormat.CSV:
            params = new URLSearchParams({
                format: "tilecsv",
                total: "1",
                "term-filter": JSON.stringify([
                    {
                        inverted: false,
                        type: "string",
                        context: "",
                        context_label: "",
                        id: resourceInstanceId,
                        value: resourceInstanceId,
                        selected: true,
                    },
                ]),
            });

            window.open(
                arches.urls.export_results + "?" + params.toString(),
                "_blank",
            );
            break;
    }
}
</script>

<template>
    <div class="export-links">
        <div class="export-links-label">
            {{ $gettext("Export as:") }}
        </div>
        <Button
            v-for="exportFormat in exportFormats"
            :key="exportFormat"
            :label="exportFormat"
            :aria-label="
                $gettext('Export as: %{exportFormat}', { exportFormat })
            "
            variant="link"
            @click="exportData(exportFormat as ExportFormat)"
        >
        </Button>
    </div>
</template>

<style scoped>
.export-links {
    display: flex;
    justify-content: flex-end;
    padding-inline-end: 20px;
    background-color: #f8fafc;
    /* background-color: var(--p-panel-background); */
}
.export-links-label {
    padding: 10px;
    color: var(--p-text-color);
}
@media print {
    .export-links {
        display: none;
    }
}
</style>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Message from "primevue/message";

import {
    ASC,
    ROWS_PER_PAGE_OPTIONS,
} from "@/arches_modular_reports/constants.ts";
import { fetchRelatedResourceData } from "@/arches_modular_reports/ModularReport/api.ts";
import FileListViewer from "@/arches_modular_reports/ModularReport/components/FileListViewer.vue";
import type { FileReference } from "@/arches_component_lab/datatypes/file-list/types";

type FileLink = FileReference & { is_file?: boolean };
type DataCell = { display_value: string; links?: FileLink[] };
export type DataRow = { id: string | number } & Record<string, DataCell>;

const props = defineProps<{
    component: {
        config: {
            node_aliases: string[];
            graph_slug: string;
            custom_labels: Record<string, string>;
        };
    };
    resourceInstanceId: string;
}>();

const { $gettext } = useGettext();

const queryTimeoutValue = 500;
let timeout: ReturnType<typeof setTimeout> | null = null;

const rowsPerPage = ref(ROWS_PER_PAGE_OPTIONS[0]);
const currentPage = ref(1);
const query = ref("");
const sortField = ref("@relation_name");
const direction = ref(ASC);
const currentlyDisplayedTableData = ref<DataRow[]>([]);
const searchResultsTotalCount = ref(0);
const isLoading = ref(false);
const hasLoadingError = ref(false);
const graphName = ref("");
const widgetLabelLookup = ref<Record<string, string>>({});
const resettingToFirstPage = ref(false);

const pageNumberToNodegroupTileData = ref<Record<number, DataRow[]>>({});

const isEmpty = computed(
    () =>
        !isLoading.value &&
        !query.value &&
        !searchResultsTotalCount.value &&
        !timeout,
);

const columnData = computed(() => {
    return [
        // {
        //     nodeAlias: "@relation_name",
        //     widgetLabel: "Relation Name",
        // },
        // {
        //     nodeAlias: "@display_name",
        //     widgetLabel: "Display Name",
        // },
        ...props.component.config.node_aliases.map((nodeAlias: string) => {
            return {
                nodeAlias,
                widgetLabel:
                    props.component.config.custom_labels?.[nodeAlias] ??
                    widgetLabelLookup.value[nodeAlias] ??
                    nodeAlias,
            };
        }),
    ];
});

watch(query, () => {
    if (timeout) {
        clearTimeout(timeout);
    }

    timeout = setTimeout(() => {
        pageNumberToNodegroupTileData.value = {};
        resettingToFirstPage.value = true;
        fetchData(1);
    }, queryTimeoutValue);
});

watch([direction, sortField, rowsPerPage], () => {
    pageNumberToNodegroupTileData.value = {};
    resettingToFirstPage.value = true;
    fetchData(1);
});

watch(currentPage, () => {
    if (currentPage.value in pageNumberToNodegroupTileData.value) {
        currentlyDisplayedTableData.value =
            pageNumberToNodegroupTileData.value[currentPage.value];
    } else {
        resettingToFirstPage.value = false;
        fetchData(currentPage.value);
    }
});

async function fetchData(requested_page: number = 1) {
    isLoading.value = true;

    try {
        const { results, page, total_count, graph_name, widget_labels } =
            await fetchRelatedResourceData(
                props.resourceInstanceId,
                props.component.config.graph_slug,
                props.component.config.node_aliases,
                rowsPerPage.value,
                requested_page,
                sortField.value,
                direction.value,
                query.value,
            );

        pageNumberToNodegroupTileData.value[page] = results;
        currentlyDisplayedTableData.value = results;
        currentPage.value = page;
        searchResultsTotalCount.value = total_count;
        graphName.value = graph_name;
        widgetLabelLookup.value = widget_labels;
    } catch (error) {
        hasLoadingError.value = true;
        throw error;
    } finally {
        isLoading.value = false;
    }
}

function formatDisplayValue(display_value: string) {
    try {
        const val = JSON.parse(display_value);
        if (Array.isArray(val)) {
            return val.join(", ");
        } else {
            return val;
        }
    } catch {
        return display_value;
    }
}

onMounted(fetchData);
</script>

<template>
    <Message
        v-if="hasLoadingError"
        size="large"
        severity="error"
        icon="pi pi-times-circle"
    >
        {{ $gettext("An error occurred while fetching data.") }}
    </Message>
    <div
        v-else-if="isEmpty"
        class="section-table"
    >
        <div
            style="display: none"
            class="p-datatable-header section-table-header"
        >
            <h4>{{ graphName }}</h4>
        </div>
        <div class="no-data-found">
            {{ $gettext("No data found.") }}
        </div>
    </div>
    <div
        v-for="row in currentlyDisplayedTableData"
        v-else
        :key="row.id"
    >
        <div
            v-for="field in columnData"
            :key="field.nodeAlias"
        >
            <template v-if="row[field.nodeAlias]?.links?.length">
                <FileListViewer
                    v-if="row[field.nodeAlias]?.links?.[0]?.is_file"
                    :file-data="row[field.nodeAlias]?.links ?? []"
                />
                <template v-else>
                    {{
                        formatDisplayValue(
                            row[field.nodeAlias]?.display_value ?? "",
                        )
                    }}
                </template>
            </template>
        </div>
    </div>
</template>

<style scoped>
.panel-content .section-table:not(:first-child) {
    padding-top: 18px;
}

.section-table-header {
    display: flex;
    align-items: center;
}

.section-table-header h4 {
    font-size: 1.8rem;
}

.section-table-header-functions {
    display: flex;
    justify-content: flex-end;
    flex-grow: 1;
}

.no-data-found {
    padding: var(--p-panel-toggleable-header-padding);
}

:deep(.p-datatable-column-sorted) {
    background: var(--p-datatable-header-cell-background);
}

:deep(.p-paginator) {
    justify-content: end;
}

.node-value-link {
    display: block;
    width: fit-content;
    font-size: inherit;
    padding: 0;
}
</style>

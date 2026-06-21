<script setup lang="ts">
import { computed, inject, onMounted, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import Message from "primevue/message";

import {
    ASC,
    DESC,
    ROWS_PER_PAGE_OPTIONS,
} from "@/arches_modular_reports/constants.ts";
import { fetchNodegroupTileData } from "@/arches_modular_reports/ModularReport/api.ts";
import FileListViewer from "@/arches_modular_reports/ModularReport/components/FileListViewer.vue";
import HierarchicalTileViewer from "@/arches_modular_reports/ModularReport/components/HierarchicalTileViewer.vue";
import { formatNumber } from "@/arches_modular_reports/ModularReport/utils.ts";
import { fieldGroupAnchorId } from "@/arches_rascolls/ModularReport/utils.ts";

import type { Ref } from "vue";
import type { DataTablePageEvent } from "primevue/datatable";
import type {
    LabelBasedCard,
    NodePresentationLookup,
    LanguageSettings,
} from "@/arches_modular_reports/ModularReport/types";

interface NodeDisplayValue {
    display_value: string | { label: string; link: string }[];
    has_links?: boolean;
    is_file?: boolean;
    file_data?: unknown[];
}

const props = defineProps<{
    component: {
        config: {
            nodegroup_alias: string;
            node_aliases: string[];
            custom_labels: Record<string, string>;
            custom_card_name: string | null;
            has_write_permission: boolean;
            empty_state_icon?: string;
            empty_state_message?: string;
            filters:
                | { alias: string; value: string; field_lookup: string }[]
                | null;
        };
    };
    resourceInstanceId: string;
}>();

const { requestCreateTile } = inject("createTile") as {
    requestCreateTile: (nodegroupAlias: string) => void;
};

const { requestSoftDeleteTile } = inject("softDeleteTile") as {
    requestSoftDeleteTile: (nodegroupAlias: string, tileId: string) => void;
};

const { $gettext } = useGettext();
const CARDINALITY_N = "n";
const queryTimeoutValue = 500;
let timeout: ReturnType<typeof setTimeout> | null = null;

const rowsPerPage = ref(ROWS_PER_PAGE_OPTIONS[0]);
const currentPage = ref(1);
const query = ref("");
const sortNodeId = ref("");
const direction = ref(ASC);
const currentlyDisplayedTableData = ref<LabelBasedCard[]>([]);
const searchResultsTotalCount = ref(0);
const unfilteredTotalCount = ref(0);
const isLoading = ref(false);
const hasLoadingError = ref(false);
const resettingToFirstPage = ref(false);
const pageNumberToNodegroupTileData = ref<Record<number, LabelBasedCard[]>>({});

const userCanEditResourceInstance = inject(
    "userCanEditResourceInstance",
) as Ref<boolean>;
const nodePresentationLookup = inject("nodePresentationLookup") as Ref<
    NodePresentationLookup | undefined
>;
const languageSettings = inject(
    "languageSettings",
    ref({ ACTIVE_LANGUAGE: "en", ACTIVE_LANGUAGE_DIRECTION: "ltr" }),
) as Ref<LanguageSettings>;
const { setSelectedNodegroupAlias } = inject("selectedNodegroupAlias") as {
    setSelectedNodegroupAlias: (nodegroupAlias: string | undefined) => void;
};
const { setSelectedTileId } = inject("selectedTileId") as {
    setSelectedTileId: (tileId: string | null | undefined) => void;
};
const { setSelectedTilePath } = inject("selectedTilePath") as {
    setSelectedTilePath: (path: string[] | null) => void;
};
const { setSelectedNodeAlias } = inject("selectedNodeAlias") as {
    setSelectedNodeAlias: (nodeAlias: string | null) => void;
};
const { setShouldShowEditor } = inject("shouldShowEditor") as {
    setShouldShowEditor: (shouldShow: boolean) => void;
};

const first = computed(() => {
    if (resettingToFirstPage.value) {
        return 0;
    }
    return (currentPage.value - 1) * rowsPerPage.value;
});

const isEmpty = computed(
    () =>
        !isLoading.value &&
        !query.value &&
        !searchResultsTotalCount.value &&
        !timeout,
);

const canEdit = computed(
    () =>
        userCanEditResourceInstance.value &&
        props.component.config.has_write_permission,
);

const shouldShowAddButton = computed(
    () =>
        canEdit.value && !isEmpty.value && cardinality.value === CARDINALITY_N,
);

const columnData = computed(() => {
    if (!nodePresentationLookup.value) {
        return [];
    }
    return props.component.config.node_aliases.map((nodeAlias) => {
        const nodeDetails = nodePresentationLookup.value![nodeAlias];
        return {
            nodeAlias: nodeAlias,
            widgetLabel:
                props.component.config.custom_labels?.[nodeAlias] ??
                nodeDetails?.widget_label ??
                nodeAlias,
            is_rich_text: nodeDetails?.is_rich_text,
            is_numeric: nodeDetails?.is_numeric,
            number_format: nodeDetails?.number_format,
        };
    });
});

const cardinality = computed(() => {
    const firstNodeAlias = props.component.config.node_aliases[0];
    if (!nodePresentationLookup.value || !firstNodeAlias) {
        return "";
    }
    return nodePresentationLookup.value[firstNodeAlias].nodegroup.cardinality;
});

const cardName = computed(() => {
    const firstNodeAlias = props.component.config.node_aliases[0];
    if (!nodePresentationLookup.value || !firstNodeAlias) {
        return "";
    }
    return (
        props.component.config.custom_card_name ??
        nodePresentationLookup.value[firstNodeAlias].card_name
    );
});

const anchorId = computed(() => fieldGroupAnchorId(props.component.config));

const emptyStateIcon = computed(
    () => props.component.config.empty_state_icon ?? "pi pi-inbox",
);

const emptyStateMessage = computed(
    () => props.component.config.empty_state_message ?? "",
);

// Render a compact single-record card (value + qualifier chips) instead of a
// table when there is exactly one plain tile.
const singleRecord = computed(() => {
    if (
        query.value ||
        searchResultsTotalCount.value !== 1 ||
        currentlyDisplayedTableData.value.length !== 1
    ) {
        return null;
    }
    const row = currentlyDisplayedTableData.value[0];
    if (row["@has_children"]) {
        return null;
    }
    const populated = columnData.value.filter((columnDatum) => {
        const cell = row[columnDatum.nodeAlias] as unknown as
            | NodeDisplayValue
            | undefined;
        if (!cell) {
            return false;
        }
        if (cell.is_file) {
            return Boolean(cell.file_data?.length);
        }
        if (cell.has_links) {
            return Boolean((cell.display_value as unknown[])?.length);
        }
        return Boolean(cell.display_value);
    });
    if (!populated.length) {
        return null;
    }
    // files and rich text read better in the table layout
    const primaryCell = row[
        populated[0].nodeAlias
    ] as unknown as NodeDisplayValue;
    if (primaryCell.is_file || populated[0].is_rich_text) {
        return null;
    }
    return {
        row,
        primary: populated[0],
        details: populated.slice(1),
        primaryLinks: primaryCell.has_links
            ? (primaryCell.display_value as { label: string; link: string }[])
            : null,
    };
});

function cellText(
    row: LabelBasedCard,
    columnDatum: (typeof columnData.value)[number],
): string {
    const cell = row[columnDatum.nodeAlias] as unknown as
        | NodeDisplayValue
        | undefined;
    if (!cell?.display_value) {
        return "";
    }
    if (cell.has_links) {
        return (cell.display_value as { label: string }[])
            .map((item) => item.label)
            .join(", ");
    }
    if (columnDatum.is_numeric) {
        return formatNumber(
            cell.display_value as string,
            columnDatum.number_format,
            languageSettings.value,
        );
    }
    return cell.display_value as string;
}

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

watch([direction, sortNodeId, rowsPerPage], () => {
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

onMounted(fetchData);

async function fetchData(page: number = 1) {
    isLoading.value = true;

    try {
        const {
            results,
            page: fetchedPage,
            total_count: totalCount,
        } = await fetchNodegroupTileData(
            props.resourceInstanceId,
            props.component.config.nodegroup_alias,
            rowsPerPage.value,
            page,
            sortNodeId.value,
            direction.value,
            query.value,
            props.component.config?.filters,
        );

        pageNumberToNodegroupTileData.value[fetchedPage] = results;
        currentlyDisplayedTableData.value = results;
        currentPage.value = fetchedPage;
        searchResultsTotalCount.value = totalCount;
        if (!query.value) {
            unfilteredTotalCount.value = totalCount;
        }
    } catch (error) {
        hasLoadingError.value = true;
        throw error;
    } finally {
        isLoading.value = false;
    }
}

function onPageTurn(event: DataTablePageEvent) {
    currentPage.value = resettingToFirstPage.value ? 1 : event.page + 1;
    rowsPerPage.value = event.rows;
}

function onUpdateSortField(event: string) {
    sortNodeId.value = nodePresentationLookup.value![event].nodeid;
}

function onUpdateSortOrder(event: number | undefined) {
    if (event === 1) {
        direction.value = ASC;
    } else if (event === -1) {
        direction.value = DESC;
    }
}

function rowClass(data: LabelBasedCard) {
    return [{ "no-children": data["@has_children"] === false }];
}

function initiateEdit(tileId: string | null) {
    setSelectedNodegroupAlias(props.component.config.nodegroup_alias);
    setSelectedNodeAlias(props.component.config.node_aliases[0]);

    // We cannot derive the path from the tileid alone, so clear it.
    setSelectedTilePath(null);
    setSelectedTileId(tileId);

    if (!tileId) {
        requestCreateTile(props.component.config.nodegroup_alias);
    }

    setShouldShowEditor(true);
}

function initiateSoftDelete(tileId: string) {
    initiateEdit(tileId);
    requestSoftDeleteTile(props.component.config.nodegroup_alias, tileId);
}
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
        v-else
        :id="anchorId"
        class="field-group"
        :class="{ 'has-data': !isEmpty }"
    >
        <div class="field-label-row">
            <h4 class="field-label">{{ cardName }}</h4>
            <Button
                v-if="shouldShowAddButton"
                :label="$gettext('Add %{cardName}', { cardName })"
                icon="pi pi-plus"
                severity="secondary"
                variant="text"
                size="small"
                @click="initiateEdit(null)"
            />
        </div>

        <div
            v-if="isEmpty"
            class="field-group-empty"
        >
            <div class="empty-icon">
                <i
                    :class="emptyStateIcon"
                    aria-hidden="true"
                ></i>
            </div>
            <div class="empty-headline">
                {{
                    $gettext("No %{cardName} recorded", {
                        cardName: cardName.toLowerCase(),
                    })
                }}
            </div>
            <p
                v-if="emptyStateMessage"
                class="empty-sub"
            >
                {{ emptyStateMessage }}
            </p>
            <Button
                v-if="canEdit"
                :label="$gettext('Add %{cardName}', { cardName })"
                icon="pi pi-plus"
                size="small"
                @click="initiateEdit(null)"
            />
        </div>

        <div
            v-else-if="singleRecord"
            class="record-single"
        >
            <div class="record-single-body">
                <template v-if="singleRecord.primaryLinks">
                    <Button
                        v-for="item in singleRecord.primaryLinks"
                        :key="item.link"
                        :href="item.link"
                        target="_blank"
                        as="a"
                        variant="link"
                        :label="item.label"
                        class="record-value-link"
                    />
                </template>
                <span
                    v-else
                    class="record-value"
                >
                    {{ cellText(singleRecord.row, singleRecord.primary) }}
                </span>
                <div
                    v-if="singleRecord.details.length"
                    class="record-details"
                >
                    <div
                        v-for="detail in singleRecord.details"
                        :key="detail.nodeAlias"
                        class="record-detail"
                    >
                        <span class="record-detail-label">
                            {{ detail.widgetLabel }}
                        </span>
                        <span class="record-detail-value">
                            {{ cellText(singleRecord.row, detail) }}
                        </span>
                    </div>
                </div>
            </div>
            <div
                v-if="canEdit"
                class="row-actions"
            >
                <Button
                    icon="pi pi-pencil"
                    variant="text"
                    rounded
                    :aria-label="$gettext('Edit %{cardName}', { cardName })"
                    @click="initiateEdit(singleRecord.row['@tile_id'])"
                />
                <Button
                    icon="pi pi-trash"
                    variant="text"
                    rounded
                    severity="danger"
                    :aria-label="$gettext('Delete %{cardName}', { cardName })"
                    @click="initiateSoftDelete(singleRecord.row['@tile_id'])"
                />
            </div>
        </div>

        <DataTable
            v-else
            class="field-group-table"
            :value="currentlyDisplayedTableData"
            :loading="isLoading"
            :total-records="searchResultsTotalCount"
            :expanded-rows="[]"
            :first="first"
            :row-class="rowClass"
            :always-show-paginator="
                searchResultsTotalCount >
                Math.min(rowsPerPage, ROWS_PER_PAGE_OPTIONS[0])
            "
            :lazy="true"
            :rows="rowsPerPage"
            :rows-per-page-options="ROWS_PER_PAGE_OPTIONS"
            :sortable="cardinality === CARDINALITY_N"
            size="small"
            striped-rows
            paginator
            @page="onPageTurn"
            @update:first="resettingToFirstPage = false"
            @update:sort-field="onUpdateSortField"
            @update:sort-order="onUpdateSortOrder"
        >
            <template
                v-if="cardinality === CARDINALITY_N && unfilteredTotalCount > 5"
                #header
            >
                <div class="field-group-table-functions">
                    <IconField>
                        <InputIcon
                            class="pi pi-search"
                            aria-hidden="true"
                            style="font-size: 1rem"
                        />
                        <InputText
                            v-model="query"
                            size="small"
                            :placeholder="$gettext('Search')"
                            :aria-label="$gettext('Search')"
                        />
                    </IconField>
                </div>
            </template>
            <template #empty>
                <Message
                    size="large"
                    severity="info"
                    icon="pi pi-info-circle"
                >
                    {{ $gettext("No results match your search.") }}
                </Message>
            </template>

            <Column
                expander
                class="expander-column"
            />
            <Column
                v-for="columnDatum of columnData"
                :key="columnDatum.nodeAlias"
                :field="columnDatum.nodeAlias"
                :header="columnDatum.widgetLabel"
                :sortable="cardinality === CARDINALITY_N"
            >
                <template #body="{ data, field }">
                    <div
                        :style="{
                            maxHeight: data[field as string]?.file_data
                                ? '32rem'
                                : '12rem',
                            overflow: 'auto',
                        }"
                    >
                        <template v-if="data[field as string]?.has_links">
                            <Button
                                v-for="item in data[field as string]
                                    .display_value"
                                :key="item.link"
                                :href="item.link"
                                target="_blank"
                                as="a"
                                variant="link"
                                :label="item.label"
                                style="display: block; width: fit-content"
                            />
                        </template>
                        <FileListViewer
                            v-else-if="data[field as string]?.is_file"
                            :file-data="data[field as string].file_data"
                        />
                        <template v-else-if="columnDatum.is_rich_text">
                            <span
                                class="rich-text-container"
                                v-html="data[field as string]?.display_value"
                            ></span>
                        </template>
                        <template v-else-if="columnDatum.is_numeric">
                            {{
                                formatNumber(
                                    data[field as string]?.display_value,
                                    columnDatum.number_format,
                                    languageSettings,
                                )
                            }}
                        </template>
                        <template v-else>
                            {{ data[field as string]?.display_value }}
                        </template>
                    </div>
                </template>
            </Column>
            <Column
                v-if="canEdit"
                class="edit-button-column"
            >
                <template #body="{ data }">
                    <div class="row-actions">
                        <Button
                            icon="pi pi-pencil"
                            variant="text"
                            rounded
                            :aria-label="$gettext('Edit')"
                            @click="initiateEdit(data['@tile_id'])"
                        />
                        <Button
                            icon="pi pi-trash"
                            variant="text"
                            rounded
                            severity="danger"
                            :aria-label="$gettext('Delete')"
                            @click="initiateSoftDelete(data['@tile_id'])"
                        />
                    </div>
                </template>
            </Column>
            <template #expansion="slotProps">
                <HierarchicalTileViewer
                    :nodegroup-alias="props.component.config.nodegroup_alias"
                    :tile-id="slotProps.data['@tile_id']"
                    :custom-labels="props.component.config.custom_labels"
                    :show-empty-nodes="true"
                />
            </template>
        </DataTable>
    </div>
</template>

<style scoped>
.field-group {
    padding: 0.75rem 0;
}

.field-group:not(:last-child) {
    border-bottom: 1px solid var(--p-content-border-color, #e2e8f0);
}

.field-label-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.25rem;
}

.field-label {
    margin: 0;
    font-size: 1.36rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--p-text-muted-color, #475467);
}

.field-group-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
    padding: 1.75rem 1rem;
    border: 1px solid var(--p-content-border-color, #e2e8f0);
    border-radius: 8px;
    background: var(--p-surface-50, #f8fafc);
    text-align: center;
}

.field-group-empty .empty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3.4rem;
    height: 3.4rem;
    border-radius: 50%;
    background: var(--p-surface-100, #f1f5f9);
    margin-bottom: 0.25rem;
}

.field-group-empty .empty-icon i {
    font-size: 1.6rem;
    color: var(--p-text-muted-color, #94a3b8);
}

.field-group-empty .empty-headline {
    font-weight: 600;
    color: var(--p-text-muted-color, #64748b);
}

.field-group-empty .empty-sub {
    margin: 0 0 0.5rem 0;
    max-width: 48rem;
    color: var(--p-text-muted-color, #94a3b8);
    font-size: 1.2rem;
}

.record-single {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.6rem 0.9rem;
    border: 1px solid var(--p-primary-200, #99f6e4);
    border-radius: 6px;
    background: var(--p-primary-50, #f0fdfa);
}

.record-single-body {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-width: 0;
}

.record-value {
    font-size: 1.4rem;
    color: var(--p-text-color, #1e293b);
    overflow-wrap: anywhere;
}

.record-value-link {
    padding: 0;
    width: fit-content;
}

.record-details {
    display: grid;
    grid-template-columns: max-content 1fr;
    column-gap: 1.25rem;
    row-gap: 0.2rem;
}

.record-detail {
    display: contents;
}

.record-detail-label {
    color: var(--p-text-muted-color, #64748b);
    font-size: 1.15rem;
}

.record-detail-value {
    color: var(--p-text-color, #1e293b);
    font-size: 1.15rem;
    overflow-wrap: anywhere;
}

.row-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.15rem;
    flex-shrink: 0;
    opacity: 0.55;
    transition: opacity 0.15s;
}

tr:hover .row-actions,
.record-single:hover .row-actions,
.row-actions:focus-within {
    opacity: 1;
}

.row-actions :deep(.p-button-icon) {
    font-size: 1.4rem;
}

.record-single :deep(.p-button-link .p-button-label) {
    color: var(--p-primary-800, #115e59);
}

.field-group-table-functions {
    display: flex;
    justify-content: flex-end;
}

:deep(.p-datatable-table) {
    table-layout: fixed;
}

:deep(.expander-column) {
    width: 3rem;
}

:deep(.edit-button-column) {
    width: 8rem;
}

.rich-text-container {
    max-height: 12rem;
    overflow: scroll;
    display: block;
    max-width: 75vw;
}

:deep(.p-datatable-column-sorted) {
    background: var(--p-datatable-header-cell-background);
}

:deep(.no-children .p-datatable-row-toggle-button) {
    visibility: hidden;
}

:deep(.p-paginator) {
    justify-content: end;
}

.p-button-link {
    padding: 0;
}

@media print {
    .field-group-table-functions,
    .row-actions {
        display: none;
    }
}
</style>

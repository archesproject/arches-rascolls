<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Message from "primevue/message";
import Tag from "primevue/tag";

import { fetchNodeTileData } from "@/arches_modular_reports/ModularReport/api.ts";
import { truncateDisplayData } from "@/arches_modular_reports/ModularReport/utils.ts";
import {
    fetchLifecycleState,
    fetchResourceLastEdited,
    updateLifecycleState,
} from "@/arches_rascolls/ModularReport/api.ts";
import ReportToolbar from "@/arches_rascolls/ModularReport/components/ReportToolbar.vue";

import type { Ref } from "vue";
import type {
    NodeValueDisplayDataLookup,
    SectionContent,
} from "@/arches_modular_reports/ModularReport/types";

const resourceInstanceId = inject("resourceInstanceId") as string;

const props = defineProps<{ component: SectionContent }>();

const { $gettext } = useGettext();

interface LifecycleState {
    id: string;
    name: string;
    action_label: string;
    is_initial_state: boolean;
    can_edit_resource_instances: boolean;
    next_resource_instance_lifecycle_states: LifecycleState[];
}

const hasLoadingError = ref(false);
const displayDataByAlias: Ref<NodeValueDisplayDataLookup | null> = ref(null);
const lastEdited = ref<string | null>(null);
const userIsReviewer = ref(false);
const lifecycleState = ref<LifecycleState | null>(null);
const lifecycleError = ref("");
const isUpdatingLifecycle = ref(false);

const lifecycleSeverity = computed(() => {
    if (!lifecycleState.value) {
        return "secondary";
    }
    if (lifecycleState.value.is_initial_state) {
        return "warn";
    }
    if (lifecycleState.value.can_edit_resource_instances) {
        return "success";
    }
    return "secondary";
});

const descriptorAliases = computed(() => {
    const matches = props.component.config.descriptor.matchAll(/<(.*?)>/g);
    return [
        ...matches.map((match: RegExpMatchArray) => {
            return match[1];
        }),
    ];
});

const locationAliases = computed<string[]>(
    () => props.component.config.location_node_aliases ?? [],
);

const maxTileLimit = computed(() => {
    const limits = props.component.config.descriptor.node_alias_options?.map(
        (option: { limit?: number; separator?: string }) => option.limit,
    );
    return Math.max(limits) || 1;
});

const descriptor = computed(() => {
    if (!displayDataByAlias.value) {
        return null;
    }

    let returnVal = props.component.config.descriptor;

    descriptorAliases.value.forEach((alias: string) => {
        const options = props.component.config.node_alias_options?.[alias];
        const limit = options?.limit ?? 1;
        const separator = options?.separator ?? ", ";
        const truncatedDisplayValues = truncateDisplayData(
            displayDataByAlias.value![alias],
            limit,
        ).flatMap((data) => data.display_values);
        returnVal = returnVal.replace(
            `<${alias}>`,
            truncatedDisplayValues.join(separator),
        );
    });

    returnVal =
        returnVal.split(" ").length > 30
            ? returnVal.split(" ").slice(0, 30).join(" ") + "..."
            : returnVal;

    document.title = returnVal;
    return returnVal;
});

const locationText = computed(() => {
    if (!displayDataByAlias.value) {
        return "";
    }
    return locationAliases.value
        .flatMap((alias) =>
            (displayDataByAlias.value![alias] ?? []).flatMap(
                (data) => data.display_values,
            ),
        )
        .filter(Boolean)
        .join(" | ");
});

const lastEditedText = computed(() => {
    if (!lastEdited.value) {
        return "—";
    }
    return new Date(lastEdited.value).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    });
});

async function fetchData() {
    try {
        displayDataByAlias.value = await fetchNodeTileData(
            resourceInstanceId,
            [...descriptorAliases.value, ...locationAliases.value],
            maxTileLimit.value,
        );
        hasLoadingError.value = false;
    } catch {
        hasLoadingError.value = true;
    }
}

async function fetchLastEdited() {
    try {
        const data = await fetchResourceLastEdited(resourceInstanceId);
        lastEdited.value = data.last_edited;
        userIsReviewer.value = data.user_is_reviewer;
    } catch (error) {
        lastEdited.value = null;
        console.error("Unable to fetch last-edited data:", error);
    }
}

async function fetchLifecycle() {
    try {
        lifecycleState.value = await fetchLifecycleState(resourceInstanceId);
    } catch (error) {
        lifecycleState.value = null;
        console.error("Unable to fetch lifecycle state:", error);
    }
}

async function advanceLifecycle(nextState: LifecycleState) {
    isUpdatingLifecycle.value = true;
    lifecycleError.value = "";
    try {
        await updateLifecycleState(resourceInstanceId, nextState.id);
        await fetchLifecycle();
    } catch (error) {
        lifecycleError.value =
            error instanceof Error
                ? error.message
                : $gettext("Unable to update lifecycle state");
    } finally {
        isUpdatingLifecycle.value = false;
    }
}

function printReport() {
    window.print();
}

onMounted(() => {
    fetchData();
    fetchLastEdited();
    fetchLifecycle();
});
</script>
<template class="report-header">
    <div style="background-color: #f8fafc">
        <div class="header-row">
            <div>
                <div class="title-row">
                    <div class="report-title">{{ descriptor }}</div>
                    <Tag
                        v-if="lifecycleState"
                        :value="lifecycleState.name"
                        :severity="lifecycleSeverity"
                        rounded
                    />
                </div>
                <div
                    v-if="component.config.subtitle"
                    class="report-subtitle"
                >
                    {{ component.config.subtitle }}
                </div>
            </div>
            <div class="header-actions">
                <Button
                    :label="$gettext('Print')"
                    icon="pi pi-print"
                    severity="secondary"
                    variant="outlined"
                    @click="printReport"
                />
                <template
                    v-if="
                        userIsReviewer &&
                        lifecycleState?.next_resource_instance_lifecycle_states
                            ?.length
                    "
                >
                    <Button
                        v-for="nextState in lifecycleState.next_resource_instance_lifecycle_states"
                        :key="nextState.id"
                        :label="
                            nextState.action_label ||
                            $gettext('Move to %{name}', {
                                name: nextState.name,
                            })
                        "
                        icon="pi pi-arrow-right"
                        icon-pos="right"
                        :loading="isUpdatingLifecycle"
                        @click="advanceLifecycle(nextState)"
                    />
                </template>
            </div>
        </div>
        <div class="header-meta">
            <div class="meta-item">
                <span class="meta-label">{{ $gettext("Location:") }}</span>
                <span>{{ locationText || "—" }}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">{{ $gettext("Last edited:") }}</span>
                <span>{{ lastEditedText }}</span>
            </div>
            <ReportToolbar
                :export-formats="['json', 'csv', 'json-ld']"
                :resource-instance-id="resourceInstanceId"
            >
            </ReportToolbar>
        </div>
    </div>
    <Message
        v-if="hasLoadingError"
        severity="error"
        style="width: fit-content"
    >
        {{ $gettext("Unable to fetch resource") }}
    </Message>
    <Message
        v-if="lifecycleError"
        severity="error"
        closable
        style="width: fit-content"
    >
        {{ lifecycleError }}
    </Message>
</template>
<style scoped>
.header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    column-gap: 1.5rem;
    row-gap: 0.5rem;
    padding: 2rem 2.4rem 1.4rem;
    min-width: 0;
}

.report-header {
    border: 0;
    border-radius: 0;
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: unset;
}

.header-row .report-title {
    font-size: 2.2rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 1.2;
    color: var(--p-text-color, #101828);
}

.report-subtitle {
    color: var(--p-text-muted-color, #667085);
    font-size: 1.2rem;
    margin-top: 0.2rem;
}

.title-row {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.header-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    column-gap: 2.4rem;
    row-gap: 0.6rem;
    padding: 1.2rem 2.4rem;
    border-top: 1px solid var(--p-content-border-color, #e5e7eb);
    border-bottom: 1px solid var(--p-content-border-color, #e5e7eb);
    font-size: 1.2rem;
    color: var(--p-text-muted-color, #667085);
}

.meta-item {
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
    min-width: 0;
}

.meta-label {
    font-weight: 600;
    white-space: nowrap;
}

@media print {
    .report-header {
        position: unset;
    }
}
</style>

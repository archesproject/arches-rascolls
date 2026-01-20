<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Message from "primevue/message";
import Card from "primevue/card";

import { fetchNodeTileData } from "@/arches_modular_reports/ModularReport/api.ts";
import { truncateDisplayData } from "@/arches_modular_reports/ModularReport/utils.ts";

import type { Ref } from "vue";
import type {
    NodeValueDisplayDataLookup,
    SectionContent,
} from "@/arches_modular_reports/ModularReport/types";

const resourceInstanceId = inject("resourceInstanceId") as string;

const props = defineProps<{ component: SectionContent }>();

const { $gettext } = useGettext();

const hasLoadingError = ref(false);
const displayDataByAlias: Ref<NodeValueDisplayDataLookup | null> = ref(null);

const descriptorAliases = computed(() => {
    const matches = props.component.config.descriptor.matchAll(/<(.*?)>/g);
    return [
        ...matches.map((match: RegExpMatchArray) => {
            return match[1];
        }),
    ];
});

const maxTileLimit = computed(() => {
    const limits = props.component.config.descriptor.node_alias_options?.map(
        (option: { limit?: number; separator?: string }) => option.limit,
    );
    return Math.max(limits) || 1;
});

const descriptor = computed(() => {
    console.log('yo yo!');
    if (!displayDataByAlias.value) {
        return null;
    }

    let returnVal = props.component.config.descriptor;

    descriptorAliases.value.forEach((alias: string) => {
        console.log('alias', alias);
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

async function fetchData() {
    try {
        displayDataByAlias.value = await fetchNodeTileData(
            resourceInstanceId,
            descriptorAliases.value,
            maxTileLimit.value,
        );
        hasLoadingError.value = false;
    } catch {
        hasLoadingError.value = true;
    }
}

onMounted(fetchData);
</script>

<template>
    <Card class="report-header">
        <template #content>
            <div class="header-toolbar">
                <div class="header-row">
                    <h2>{{ descriptor }}</h2>
                </div>
            </div>
        </template>
        <Message
            v-if="hasLoadingError"
            severity="error"
            style="width: fit-content"
        >
            {{ $gettext("Unable to fetch resource") }}
        </Message>
    </Card>
</template>

<style scoped>

.header-toolbar {
	min-height: 3rem;
	height: auto;
	background: var(--p-header-background);
	border-bottom: 0.0625rem solid var(--p-header-border);
	padding-inline-start: 1rem;
	padding-inline-end: 1rem;
	padding-top: 0.375rem;
	padding-bottom: 0.375rem;
	box-sizing: border-box;
}

.header-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	column-gap: 1rem;
	row-gap: 0.5rem;
	padding: 0.2rem 0 0 0;
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

.report-header h2 {
    font-size: 2rem;
    margin: 1rem;
}

@media print {
    .report-header {
        position: unset;
    }
}
</style>

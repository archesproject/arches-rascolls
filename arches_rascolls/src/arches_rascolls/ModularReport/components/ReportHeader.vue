<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Message from "primevue/message";
import Card from "primevue/card";

import { fetchNodeTileData } from "@/arches_modular_reports/ModularReport/api.ts";
import { truncateDisplayData } from "@/arches_modular_reports/ModularReport/utils.ts";
import ReportToolbar from "@/arches_rascolls/ModularReport/components/ReportToolbar.vue";


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
    <template #content class="report-header">
        <div style="background-color: #f8fafc;">
            <div class="header-row">
                <div class="report-title">{{ descriptor }}</div>
                <ReportToolbar
                        :export-formats='["json", "csv"]'
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
    </template>
<style scoped>

.header-row {
    display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	column-gap: 1rem;
	row-gap: 0.5rem;
	padding: 0.2rem 0 0 0;
	min-width: 0;
    border-bottom: 0.0625rem solid #d7d7d7;
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
    font-size: 2.1rem;
    font-weight: 600;
    color: #474747;
    padding-left: 1rem;
}

@media print {
    .report-header {
        position: unset;
    }
}
</style>

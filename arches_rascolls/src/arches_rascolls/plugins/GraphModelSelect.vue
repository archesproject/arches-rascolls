<template>
    <div style="display: flex; align-items: center; gap: 0.5rem">
        <label for="graph-model-select">Resource Model</label>
        <Select
            id="graph-model-select"
            :model-value="modelValue"
            :options="graphOptions"
            option-label="label"
            option-value="value"
            :loading="loading"
            placeholder="Select a resource model..."
            style="min-width: 20rem"
            @update:model-value="$emit('update:modelValue', $event)"
        />
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import arches from "arches";
import Select from "primevue/select";

import type { GraphModel } from "@/arches_rascolls/plugins/GraphRelationViewer.vue";

const props = defineProps<{
    modelValue: string | null;
    graphs: GraphModel[];
    loading: boolean;
}>();

defineEmits<{
    "update:modelValue": [value: string | null];
}>();

function resolveGraphName(name: GraphModel["name"]): string {
    if (typeof name === "string") return name;
    return (
        name[arches.activeLanguage] ??
        name["en"] ??
        Object.values(name)[0] ??
        ""
    );
}

const graphOptions = computed(() =>
    props.graphs.map((g) => ({
        label: resolveGraphName(g.name),
        value: g.graphid,
    })),
);
</script>

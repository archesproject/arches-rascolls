<template>
    <div style="position: relative; height: 100%; background-color: #fff">
        <GraphNetwork
            v-if="selectedGraphId"
            :graphid="selectedGraphId"
            :all-graphs="resourceModels"
            style="height: 100%"
        />
        <div style="position: absolute; top: 8px; left: 8px; z-index: 10">
            <GraphModelSelect
                v-model="selectedGraphId"
                :graphs="resourceModels"
                :loading="loadingGraphs"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import arches from "arches";

import GraphModelSelect from "@/arches_rascolls/plugins/GraphModelSelect.vue";
import GraphNetwork from "@/arches_rascolls/plugins/GraphNetwork.vue";

export interface GraphModel {
    graphid: string;
    name: Record<string, string> | string;
    isresource: boolean;
}

const resourceModels = ref<GraphModel[]>([]);
const selectedGraphId = ref<string | null>(null);
const loadingGraphs = ref(false);

onMounted(async () => {
    loadingGraphs.value = true;
    try {
        const response = await fetch(arches.urls.graphs_api);
        if (!response.ok) throw new Error(response.statusText);
        const data = await response.json();
        resourceModels.value = (data as GraphModel[]).filter(
            (g) => g.isresource,
        );
    } catch (e) {
        console.error("Failed to load graph models:", e);
    } finally {
        loadingGraphs.value = false;
    }
});
</script>

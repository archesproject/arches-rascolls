<template>
    <div style="position: relative; height: 100%; min-height: 400px">
        <div
            v-if="loading"
            style="
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            "
        >
            Loading...
        </div>
        <div
            v-else-if="error"
            style="
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                color: red;
            "
        >
            {{ error }}
        </div>
        <div
            ref="cyContainer"
            style="
                height: 100%;
                width: 100%;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #000;
            "
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, nextTick } from "vue";
import arches from "arches";
import cytoscape from "cytoscape";

import type { GraphModel } from "@/arches_rascolls/plugins/GraphRelationViewer.vue";

const props = defineProps<{
    graphid: string;
    allGraphs: GraphModel[];
}>();

const cyContainer = ref<HTMLElement | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

let cy: cytoscape.Core | null = null;

interface NodeConfig {
    graphs?: { graphid: string }[];
}

interface ArchesNode {
    nodeid: string;
    name: string;
    datatype: string;
    config: NodeConfig | null;
}

function resolveGraphName(graphid: string): string {
    const match = props.allGraphs.find((g) => g.graphid === graphid);
    if (!match) return graphid;
    const name = match.name;
    if (typeof name === "string") return name;
    return (
        name[arches.activeLanguage] ??
        name["en"] ??
        Object.values(name)[0] ??
        graphid
    );
}

function buildElements(
    rootGraphId: string,
    nodes: Record<string, ArchesNode>,
): cytoscape.ElementDefinition[] {
    const elements: cytoscape.ElementDefinition[] = [];
    const seenGraphIds = new Set<string>();

    seenGraphIds.add(rootGraphId);
    elements.push({
        data: {
            id: rootGraphId,
            label: resolveGraphName(rootGraphId),
        },
        classes: "root",
    });

    for (const node of Object.values(nodes)) {
        if (
            node.datatype !== "resource-instance" &&
            node.datatype !== "resource-instance-list"
        ) {
            continue;
        }

        const relatedGraphs = node.config?.graphs ?? [];
        for (const rel of relatedGraphs) {
            const targetId = rel.graphid;

            if (!seenGraphIds.has(targetId)) {
                seenGraphIds.add(targetId);
                elements.push({
                    data: {
                        id: targetId,
                        label: resolveGraphName(targetId),
                    },
                });
            }

            elements.push({
                data: {
                    id: `${rootGraphId}-${node.nodeid}-${targetId}`,
                    source: rootGraphId,
                    target: targetId,
                    label: node.name,
                },
            });
        }
    }

    return elements;
}

function initCytoscape(elements: cytoscape.ElementDefinition[]) {
    if (cy) {
        cy.destroy();
        cy = null;
    }

    if (!cyContainer.value) return;

    cy = cytoscape({
        container: cyContainer.value,
        elements,
        style: [
            {
                selector: "node",
                style: {
                    label: "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#4a90d9",
                    color: "#fff",
                    "font-size": "12px",
                    width: 120,
                    height: 40,
                    shape: "round-rectangle",
                    "text-wrap": "wrap",
                    "text-max-width": "110px",
                },
            },
            {
                selector: "node.root",
                style: {
                    "background-color": "#2c5f9e",
                    "border-width": 3,
                    "border-color": "#1a3a6b",
                },
            },
            {
                selector: "edge",
                style: {
                    label: "data(label)",
                    "font-size": "10px",
                    color: "#555",
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "line-color": "#999",
                    "target-arrow-color": "#999",
                    "text-rotation": "autorotate",
                    "text-background-color": "#fff",
                    "text-background-opacity": 0.8,
                    "text-background-padding": "2px",
                },
            },
        ],
        layout: {
            name: "breadthfirst",
            directed: true,
            padding: 20,
            spacingFactor: 1.5,
        },
    });
}

async function loadGraph(graphid: string) {
    loading.value = true;
    error.value = null;

    try {
        const response = await fetch(arches.urls.graph_nodes(graphid));
        if (!response.ok) throw new Error(response.statusText);
        const nodes: Record<string, ArchesNode> = await response.json();

        const elements = buildElements(graphid, nodes);
        await nextTick();
        initCytoscape(elements);
    } catch (e) {
        error.value = `Failed to load graph nodes: ${(e as Error).message}`;
    } finally {
        loading.value = false;
    }
}

watch(() => props.graphid, loadGraph, { immediate: true });

onBeforeUnmount(() => {
    cy?.destroy();
    cy = null;
});
</script>

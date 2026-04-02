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
                background-color: #fff;
            "
        />
        <div
            v-if="legend.length"
            style="
                position: absolute;
                top: 8px;
                right: 8px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                pointer-events: none;
            "
        >
            <!-- Legend -->
            <div
                style="
                    background: rgba(255, 255, 255, 0.92);
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                    color: #000;
                    pointer-events: auto;
                "
            >
                <div
                    v-for="item in legend"
                    :key="item.graphid"
                    style="
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        margin-bottom: 4px;
                    "
                >
                    <span
                        :style="{
                            display: 'inline-block',
                            width: '14px',
                            height: '14px',
                            borderRadius: '3px',
                            backgroundColor: item.color,
                            border: item.isRoot
                                ? '2px solid #000'
                                : '1px solid #aaa',
                            flexShrink: '0',
                        }"
                    />
                    <span
                        :style="{
                            fontWeight: item.isRoot ? '600' : 'normal',
                            userSelect: 'text',
                        }"
                        >{{ item.label }}</span
                    >
                    <span
                        v-if="item.isRoot"
                        style="
                            font-style: italic;
                            color: #555;
                            font-weight: normal;
                        "
                        >(selected)</span
                    >
                </div>
            </div>

            <!-- Edge detail panel -->
            <div
                v-if="hoveredEdge"
                style="
                    background: rgba(255, 255, 255, 0.92);
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                    color: #000;
                    width: 220px;
                "
            >
                <div style="font-weight: 600; margin-bottom: 6px">
                    Link Details
                </div>
                <table style="border-collapse: collapse; width: 100%">
                    <tbody>
                        <tr>
                            <td
                                style="
                                    color: #555;
                                    padding-right: 8px;
                                    white-space: nowrap;
                                    vertical-align: top;
                                "
                            >
                                Node
                            </td>
                            <td
                                style="font-weight: 500; word-break: break-word"
                            >
                                {{ hoveredEdge.nodeName }}
                            </td>
                        </tr>
                        <tr>
                            <td
                                style="
                                    color: #555;
                                    padding-right: 8px;
                                    white-space: nowrap;
                                    vertical-align: top;
                                "
                            >
                                Alias
                            </td>
                            <td style="word-break: break-word">
                                {{ hoveredEdge.alias }}
                            </td>
                        </tr>
                        <tr>
                            <td
                                style="
                                    color: #555;
                                    padding-right: 8px;
                                    white-space: nowrap;
                                    vertical-align: top;
                                "
                            >
                                Type
                            </td>
                            <td>{{ hoveredEdge.datatype }}</td>
                        </tr>
                        <tr>
                            <td
                                style="
                                    color: #555;
                                    padding-right: 8px;
                                    white-space: nowrap;
                                    vertical-align: top;
                                "
                            >
                                From
                            </td>
                            <td style="word-break: break-word">
                                {{ hoveredEdge.sourceLabel }}
                            </td>
                        </tr>
                        <tr>
                            <td
                                style="
                                    color: #555;
                                    padding-right: 8px;
                                    white-space: nowrap;
                                    vertical-align: top;
                                "
                            >
                                To
                            </td>
                            <td style="word-break: break-word">
                                {{ hoveredEdge.targetLabel }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
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

interface LegendItem {
    graphid: string;
    label: string;
    color: string;
    isRoot: boolean;
}

interface HoveredEdge {
    nodeName: string;
    alias: string;
    datatype: string;
    sourceLabel: string;
    targetLabel: string;
}

const legend = ref<LegendItem[]>([]);
const hoveredEdge = ref<HoveredEdge | null>(null);

let cy: cytoscape.Core | null = null;

const PALETTE = [
    "#e05c5c",
    "#e0905c",
    "#d4c040",
    "#6abf69",
    "#4a9fd4",
    "#7c6abf",
    "#bf6aaa",
    "#5cbfb0",
    "#a0784e",
    "#8fbf4a",
];

interface NodeConfig {
    graphs?: { graphid: string }[];
}

interface ArchesNode {
    nodeid: string;
    name: string;
    alias: string;
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
): { elements: cytoscape.ElementDefinition[]; colorMap: Map<string, string> } {
    const elements: cytoscape.ElementDefinition[] = [];
    const seenGraphIds = new Set<string>();
    const colorMap = new Map<string, string>();
    let colorIndex = 0;

    function assignColor(graphid: string): string {
        if (!colorMap.has(graphid)) {
            colorMap.set(graphid, PALETTE[colorIndex % PALETTE.length]);
            colorIndex++;
        }
        return colorMap.get(graphid)!;
    }

    seenGraphIds.add(rootGraphId);
    elements.push({
        data: {
            id: rootGraphId,
            label: resolveGraphName(rootGraphId),
            color: assignColor(rootGraphId),
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
                        color: assignColor(targetId),
                    },
                });
            }

            elements.push({
                data: {
                    id: `${rootGraphId}-${node.nodeid}-${targetId}`,
                    source: rootGraphId,
                    target: targetId,
                    label: node.name,
                    nodeName: node.name,
                    alias: node.alias,
                    datatype: node.datatype,
                    sourceLabel: resolveGraphName(rootGraphId),
                    targetLabel: resolveGraphName(targetId),
                },
            });
        }
    }

    return { elements, colorMap };
}

function buildLegend(
    rootGraphId: string,
    colorMap: Map<string, string>,
): LegendItem[] {
    return Array.from(colorMap.entries()).map(([graphid, color]) => ({
        graphid,
        label: resolveGraphName(graphid),
        color,
        isRoot: graphid === rootGraphId,
    }));
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
                    "background-color": "data(color)",
                    color: "#000",
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
                    "border-width": 3,
                    "border-color": "#000",
                },
            },
            {
                selector: "edge",
                style: {
                    label: "data(label)",
                    "font-size": "10px",
                    color: "#000",
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "line-color": "#888",
                    "target-arrow-color": "#888",
                    "text-rotation": "autorotate",
                    "text-background-color": "#fff",
                    "text-background-opacity": 0.8,
                    "text-background-padding": "2px",
                },
            },
            {
                selector: "edge.hovered",
                style: {
                    "line-color": "#333",
                    "target-arrow-color": "#333",
                    width: 3,
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

    cy.on("mouseover", "edge", (event) => {
        const edge = event.target;
        edge.addClass("hovered");
        const data = edge.data();
        hoveredEdge.value = {
            nodeName: data.nodeName,
            alias: data.alias,
            datatype: data.datatype,
            sourceLabel: data.sourceLabel,
            targetLabel: data.targetLabel,
        };
    });

    cy.on("mouseout", "edge", (event) => {
        event.target.removeClass("hovered");
        hoveredEdge.value = null;
    });
}

async function loadGraph(graphid: string) {
    loading.value = true;
    error.value = null;
    legend.value = [];
    hoveredEdge.value = null;

    try {
        const response = await fetch(arches.urls.graph_nodes(graphid));
        if (!response.ok) throw new Error(response.statusText);
        const nodes: Record<string, ArchesNode> = await response.json();

        const { elements, colorMap } = buildElements(graphid, nodes);
        legend.value = buildLegend(graphid, colorMap);
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

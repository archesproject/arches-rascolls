<script setup lang="ts">
import { inject, onMounted, ref, type Ref } from "vue";
import { useGettext } from "vue3-gettext";
import Panel from "primevue/panel";
import type { NodePresentationLookup } from "@/arches_modular_reports/ModularReport/types";

import {
    importComponents,
    uniqueId,
} from "@/arches_modular_reports/ModularReport/utils.ts";

import type {
    ComponentLookup,
    CollapsibleSection,
    SectionContent,
} from "@/arches_modular_reports/ModularReport/types";

const componentLookup: ComponentLookup = {};
const { component, resourceInstanceId } = defineProps<{
    component: SectionContent;
    resourceInstanceId: string;
}>();
const nodePresentationLookup = inject("nodePresentationLookup") as Ref<
    NodePresentationLookup | undefined
>;

const { $gettext } = useGettext();
const cardName = (component: {
    config: {
        nodegroup_alias: string;
        node_aliases: string[];
        custom_labels: Record<string, string>;
        custom_card_name: string | null;
        has_write_permission: boolean;
    };
}) => {
    const firstNodeAlias = component.config.node_aliases[0];
    if (!nodePresentationLookup.value || !firstNodeAlias) {
        return "";
    }
    return (
        component.config.custom_card_name ??
        nodePresentationLookup.value[firstNodeAlias].card_name
    );
};
const linkedSections = ref<CollapsibleSection[]>([]);

onMounted(async () => {
    await importComponents(component.config.sections, componentLookup);

    for (const section of component.config.sections) {
        linkedSections.value.push({
            name: section.name,
            components: section.components.map((child: SectionContent) => ({
                ...child,
                config: { ...child.config, id: uniqueId(child) },
            })),
            collapsed: false,
        });
    }
});
</script>

<template>
    <div class="linked-section-outer-container">
        <div class="linked-section-container">
            <Panel
                v-for="linked_section in linkedSections"
                :key="linked_section.name"
                :collapsed="linked_section.collapsed"
                toggleable
                :header="$gettext('toggle section')"
                style="height: 100%; overflow: hidden"
                @toggle="linked_section.collapsed = !linked_section.collapsed"
            >
                <template #header>
                    <div class="value-header">
                        {{ cardName(linked_section.components[0]) }}
                    </div>
                </template>

                <div
                    ref="linked_sections"
                    class="panel-content"
                    style="height: 100%; overflow: auto"
                >
                    <component
                        :is="componentLookup[child.component]?.component"
                        v-for="child in linked_section.components"
                        :key="componentLookup[child.component]?.key"
                        :component="child"
                        :resource-instance-id
                    />
                </div>
            </Panel>
        </div>
    </div>
</template>

<style scoped>
.linked-section-outer-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.linked-section-button-container {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    padding: 10px 0px;
    gap: 10px;
}

button.back-to-top {
    background-color: unset;
    color: gray;
    border: solid 1px white;
    border-radius: 7rem;
    width: 2.5rem;
    height: 2.5rem;
    padding: 10px;
}

:deep(button.back-to-top span.pi) {
    font-size: 1.2rem;
}

.linked-section-container .p-panel:not(:last-child) {
    margin-bottom: 1.5rem;
}

.linked-section-container h3 {
    margin: 10px 0px;
}
</style>

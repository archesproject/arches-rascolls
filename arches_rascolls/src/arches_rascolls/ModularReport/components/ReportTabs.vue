<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { useGettext } from "vue3-gettext";

import Select from "primevue/select";
import Tab from "primevue/tab";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import TabPanel from "primevue/tabpanel";
import TabPanels from "primevue/tabpanels";

import {
    importComponents,
    uniqueId,
} from "@/arches_modular_reports/ModularReport/utils.ts";
import { fieldGroupAnchorId } from "@/arches_rascolls/ModularReport/utils.ts";

import type {
    ComponentLookup,
    NamedSection,
    SectionContent,
} from "@/arches_modular_reports/ModularReport/types";

interface FieldNavOption {
    label: string;
    tab: string;
    anchor: string;
}

interface FieldNavGroup {
    label: string;
    items: FieldNavOption[];
}

const componentLookup: ComponentLookup = {};

const { component, resourceInstanceId } = defineProps<{
    component: SectionContent;
    resourceInstanceId: string;
}>();

const { $gettext } = useGettext();

const activeTab = ref(component.config.tabs[0].name);
const visitedTabs = ref<Set<string>>(new Set([activeTab.value]));
const selectedField = ref<FieldNavOption | null>(null);

const fieldNavGroups = computed<FieldNavGroup[]>(() => {
    const groups: FieldNavGroup[] = [];
    for (const tab of component.config.tabs) {
        for (const tabComponent of tab.components) {
            for (const section of tabComponent.config?.sections ?? []) {
                const items: FieldNavOption[] = [];
                for (const child of section.components ?? []) {
                    if (!child.config?.nodegroup_alias) {
                        continue;
                    }
                    items.push({
                        label:
                            child.config.custom_card_name ??
                            child.config.nodegroup_alias,
                        tab: tab.name,
                        anchor: fieldGroupAnchorId(child.config),
                    });
                }
                if (items.length) {
                    groups.push({
                        label: `${tab.name} — ${section.name}`,
                        items,
                    });
                }
            }
        }
    }
    return groups;
});

watchEffect(() => {
    importComponents(component.config.tabs, componentLookup);

    component.config.tabs.forEach((tab: NamedSection) => {
        tab.components.forEach((child: SectionContent) => {
            child.config.id = uniqueId(child);
        });
    });
});

watch(activeTab, (tab) => {
    visitedTabs.value.add(tab);
});

function navigateToField(option: FieldNavOption | null) {
    if (!option) {
        return;
    }
    const needsTabSwitch = activeTab.value !== option.tab;
    if (needsTabSwitch) {
        activeTab.value = option.tab;
    }
    // wait for the tab panel to render before scrolling
    setTimeout(
        () => {
            document.getElementById(option.anchor)?.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
            selectedField.value = null;
        },
        needsTabSwitch ? 150 : 0,
    );
}
</script>

<template>
    <Tabs v-model:value="activeTab">
        <div class="tab-chrome">
            <TabList>
                <Tab
                    v-for="tab in component.config.tabs"
                    :key="tab.name"
                    :value="tab.name"
                >
                    {{ tab.name }}
                </Tab>
            </TabList>
            <Select
                v-model="selectedField"
                class="field-nav"
                :options="fieldNavGroups"
                option-group-label="label"
                option-group-children="items"
                option-label="label"
                filter
                size="small"
                :placeholder="$gettext('Navigate to...')"
                :aria-label="$gettext('Navigate to a field')"
                @update:model-value="navigateToField"
            />
        </div>
        <TabPanels>
            <TabPanel
                v-for="tab in component.config.tabs"
                :key="tab.name"
                :value="tab.name"
            >
                <template v-if="visitedTabs.has(tab.name)">
                    <component
                        :is="componentLookup[tabComponent.component]?.component"
                        v-for="tabComponent in tab.components"
                        :key="componentLookup[tabComponent.component]?.key"
                        :component="tabComponent"
                        :resource-instance-id="resourceInstanceId"
                    />
                </template>
            </TabPanel>
        </TabPanels>
    </Tabs>
</template>

<style scoped>
.tab-chrome {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.tab-chrome :deep(.p-tablist) {
    flex-grow: 1;
    min-width: 0;
}

.field-nav {
    min-width: 22rem;
    margin: 0 1rem;
}
</style>

<script setup lang="ts">
import { computed, ref } from "vue";

import Button from "primevue/button";

import PopupContent from "@/afrc/Search/components/InteractiveMap/components/PopupContainer/components/PopupContent.vue";

import type { Feature } from "geojson";

const props = defineProps<{ features: Feature[] }>();

const currentIndex = ref(0);

const displayedFeature = computed(() => props.features?.[currentIndex.value]);

function previousFeature() {
    if (currentIndex.value > 0) {
        currentIndex.value -= 1;
    }
}

function nextFeature() {
    if (currentIndex.value < props.features.length - 1) {
        currentIndex.value += 1;
    }
}
</script>

<template>
    <div class="feature-container">
        <PopupContent
            :resource-id="displayedFeature?.properties?.resourceinstanceid"
        />
        <div
            v-if="props.features?.length > 1"
            class="feature-footer"
        >
            <Button
                icon="pi pi-chevron-left"
                :disabled="currentIndex === 0"
                class="p-button-rounded p-button-text"
                @click="previousFeature"
            />
            <span>{{ currentIndex + 1 }} / {{ props.features.length }}</span>
            <Button
                icon="pi pi-chevron-right"
                :disabled="currentIndex === props.features.length - 1"
                class="p-button-rounded p-button-text"
                @click="nextFeature"
            />
        </div>
    </div>
</template>

<style scoped>
.feature-container {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 100%;
}

.feature-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f8f9fa;
}
</style>

<script setup lang="ts">
const { resourceId } = defineProps<{ resourceId?: string }>();
</script>

<template>
    <div
        v-if="resourceId"
        class="feature-content"
    >
        {{ resourceId }}
    </div>
</template>

<style scoped>
.feature-content {
    flex: 1;
    overflow-y: auto;
    background-color: #fff;
}
</style>

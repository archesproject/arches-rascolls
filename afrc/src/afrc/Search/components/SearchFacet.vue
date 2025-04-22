<script setup lang="ts">

defineProps({
    title: {
        type: String,
        required: true,
    },
    description: {
        type: String,
        default: null,
    },
    icon: {
        type: String,
        default: 'pi pi-address-book',
    },
    selected: {
        type: Boolean,
        default: false,
    },
    // onClick: {
    //     type: Function,
    //     required: true,
    // },
    searchString: {
        type: String,
        default: "",
        required: false,
    },
});
</script>


<template>
    <div class="facet-item" :class="{selected: selected}">
    <div class="facet-item-icon pi" :class="icon"></div>
    <h2 class="facet-item-title">{{ title }}</h2>
    <p class="facet-item-tag">
        {{ description }}
    </p>
    <a
        class="facet-item-toggle"
        href="#"
        >(click to unselect)</a
    >
</div>
</template>


<style scoped>


.facet-item {
    padding: 15px;
    border: 1px solid #ddd;
    background: #fdfdfd;
    text-align: center;
    cursor: pointer;
    width: 170px;
    height: 170px;
    border-radius: 3px;
}
.facet-item:hover {
    background-color: #f0f8ff;
    border-color: #007bff;
}

.facet-item.selected {
    background-color: #f0f8ff;
    border-color: #007bff;
    filter: drop-shadow(2px 2px 3px #ccc);
}
.facet-item-title {
    font-size: 1.05em;
    font-weight: 300;
    color: #25476a;
    margin: 0px;
}
.facet-item-icon {
    font-size: 18px;
    padding: 11px;
    border: 1px solid #aaa;
    border-radius: 50%;
    color: #aaa;
    background: #eee;
    margin-bottom: 10px;
    height: 40px;
    width: 40px;
}
.facet-item.selected .facet-item-icon {
    border: 1px solid #244768;
    border-radius: 50%;
    color: #244768;
    background: #98adc2;
}
.facet-item-tag {
    font-size: 0.85em;
    color: #aaa;
    line-height: 1.15;
    margin: 0px;
}
.facet-item-toggle {
    color: #007bff;
    font-size: 0.75em;
}
</style>
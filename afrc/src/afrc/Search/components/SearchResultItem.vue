<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps({
    searchResult: {
        type: Object,
        required: true
    }
});
</script>

<template>
    <article class="result">
        <h2>{{searchResult._source.displayname}}</h2>
        <p class="breadcrumb">(North and Central America &gt; United States &gt; Missouri &gt; Greene)</p>
        <p class="scope-note">
            <strong>Scope Note:</strong> {{searchResult._source.displaydescription}}
        </p>
        <p class="associated-concepts">
            <strong>Associated Concepts:</strong> <a href="#">slotted spoon</a>
        </p>
    </article>
</template>
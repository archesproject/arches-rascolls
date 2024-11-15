<script setup lang="ts">
import { ref, watch } from "vue";

import AutoComplete from "primevue/autocomplete";
import FloatLabel from "primevue/floatlabel";
import Button from "primevue/button";
import SelectButton from "primevue/selectbutton";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";

const componentName = "term-filter";
const props = defineProps({
    updateFilter: {
        type: Function,
        required: true
    }
});
// const emit = defineEmits(["update:filter"]);

const terms = ref([]);
const items = ref([]);
let filter = {"terms": terms};

watch(filter.terms, (newValue, oldValue) => {
  console.log("Something has changed from", oldValue, "to", newValue);
  updateQuery();
});

watch(items, (newValue, oldValue) => {
  console.log("Item has changed from", oldValue, "to", newValue);
});


const search = function(event) {
    // items.value = [...Array(10).keys()].map((item) => event.query + "-" + item);
    var queryString = new URLSearchParams();
    queryString.set("q", event.query);
    queryString.set("lang", "*");
    fetch("search/terms" + "?" + queryString.toString())
        .then(response => response.json())
        .then(data => {
            let ret = [
                { label: "Terms", items: data.terms },
                { label: "Concepts", items: data.concepts } 
            ];
            items.value = ret;
        });
};

const updateQuery = function() {
    var terms = filter.terms.value.filter(function(term){
        return term.type === "string" || term.type === "concept" || term.type === "term";
    }, this);

    const query = {};// JSON.parse(props.queryString);
    if (terms.length > 0){
        query[componentName] = terms;
        // queryObj["language"] = this.language();
    } 
    // else {
    //     delete query[componentName];
    // }
    props.updateFilter(query);
    // props.queryString.value = JSON.stringify(query);
};

</script>

<template>
    <div class="search-bar" >
        <FloatLabel variant="on">
            <AutoComplete v-model="terms" id="term-search-filter" multiple fluid 
                :suggestions="items" 
                optionLabel="text" 
                optionGroupLabel="label" 
                optionGroupChildren="items" 
                @complete="search"
            >
                <template #optiongroup="slotProps">
                    <div class="option-group">
                        <div class="pi pi-flag">{{ slotProps.option.label }}</div>
                    </div>
                </template>
                <template #option="slotProps">
                    <div class="">
                        <div>{{ slotProps.option.text }}</div>
                    </div>
                </template>
            </AutoComplete>
            <label for="term-search-filter">Search for collections...</label>

        </FloatLabel>

        <button type="submit">Search</button>
    </div>
</template>

<style scoped>
.search-bar {
    display: flex;
    margin-bottom: 1.25rem;
}
.search-bar span {
    flex: 1;
    padding: 0.625rem; /* 10px */
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 0.3125rem 0 0 0.3125rem; /* 5px */
}
.search-bar button {
    font-family: Arial, Helvetica, sans-serif;
    padding: 0.625rem 1.25rem; /* 10px 20px */
    font-size: 1rem;
    border: none;
    background-color: #ffcc33;
    color: #333;
    cursor: pointer;
    border-radius: 0 0.3125rem 0.3125rem 0;
}
.--p-autocomplete-option-group-background { 
    background-color: lightgray;
    font-family: Arial, Helvetica, sans-serif;
}
</style>

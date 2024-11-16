<script setup lang="ts">
import { ref, watch } from "vue";

import AutoComplete from "primevue/autocomplete";

const componentName = "term-filter";
const props = defineProps({
    updateFilter: {
        type: Function,
        required: true
    }
});
// const emit = defineEmits(["update:filter"]);

const items = ref([]);
const filter = ref({"terms": []});

// watch(filter.value.terms, (newValue, oldValue) => {
//   console.log("Something has changed from", oldValue, "to", newValue);
//   updateQuery();
// });
// watch(filter.value.terms, (newValue, oldValue) => {
//     console.log("Something has changed from", oldValue, "to", newValue);
//     updateQuery();    
//  }, { deep: true });    

watch(()=>filter.value.terms, (newValue, oldValue) => {
    console.log("Something has changed from", oldValue, "to", newValue);
    updateQuery();    
 }, { deep: true });


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
            Object.keys(data).forEach(key => {
                data[key].forEach(item => {
                    item.inverted = false;
                });
            });
            let ret = [
                { label: "Terms", items: data.terms },
                { label: "Concepts", items: data.concepts } 
            ];
            items.value = ret;
        });
};

const updateQuery = function() {
    var terms = filter.value.terms.filter(function(term){
        return term.type === "string" || term.type === "concept" || term.type === "term";
    }, this);

    // const query = {};// JSON.parse(props.queryString);
    // // if (terms.length > 0){
    //     query[componentName] = terms;
    //     // queryObj["language"] = this.language();
    // // } 
    // else {
    //     delete query[componentName];
    // }
    props.updateFilter(componentName, terms);
    // props.queryString.value = JSON.stringify(query);
};

</script>

<template>
    <div class="search-bar" >
        <AutoComplete 
            v-model="filter.terms" 
            multiple 
            fluid 
            :suggestions="items" 
            option-label="text" 
            option-group-label="label" 
            option-group-children="items" 
            placeholder="find ..."
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
    </div>
</template>

<style scoped>
.search-bar {
    width: 100%;
    font-size: 1rem;
}
.--p-autocomplete-option-group-background { 
    background-color: lightgray;
    font-family: Arial, Helvetica, sans-serif;
}
</style>

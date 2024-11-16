<script setup lang="ts">
import { onMounted, ref, watch } from "vue";

import Toast from "primevue/toast";
import Button from "primevue/button";

import SimpleSearchFilter from "./components/SimpleSearchFilter.vue";   
import SearchResultItem from "./components/SearchResultItem.vue";
import MapView from "./components/MapView.vue";

let query = getQueryObject(null);
let queryString = ref(JSON.stringify(query));
let searchResults = ref([]);
const showMap = ref(false);

watch(queryString, () => {
    doQuery();
});

function updateFilter(componentName: string, value: object) {
    console.log(value);
    // Test for an empty object
    function isEmpty(value) {
        if (value === null || value === undefined) {
            return true;
        }

        if (typeof value === 'string') {
            return value.trim() === '';
        }

        if (Array.isArray(value)) {
            return value.length === 0;
        }

        if (typeof value === 'object') {
            return Object.keys(value).length === 0;
        }

        return false;
    }   

    if (isEmpty(value)) {
        delete query[componentName];
    }else{
        query[componentName] = value;
    }
    queryString.value = JSON.stringify(query);
}

function getQueryObject(uri: string) {
    const url = new URL(uri || location.href);
    const params = new URLSearchParams(url.search);
    const obj = {};

    for (const [key, value] of params.entries()) {
        obj[key] = value;
    }

    return obj;
}

function objectToQueryString(obj, prefix = '') {
    return Object.entries(obj).reduce((acc, [key, value]) => {
        const encodedKey = encodeURIComponent(prefix ? `${prefix}[${key}]` : key);

        if (typeof value === 'object') {
        acc.push(objectToQueryString(value, encodedKey));
        } else {
        acc.push(`${encodedKey}=${encodeURIComponent(value)}`);
        }

        return acc;
    }, []).join('&');
}

const doQuery = function() {
    // const strippedQueryObject: object = {};
    
    const queryObj = JSON.parse(queryString.value??"{}");
    // if (self.updateRequest) { self.updateRequest.abort(); }
    
    // for (const [key, value] in Object.entries(queryObj)) {
    //     queryObj[key] = encodeURIComponent(JSON.stringify(value));
    // }
    Object.keys(queryObj).forEach(key => {
        queryObj[key] = JSON.stringify(queryObj[key]);
    });

    const qs = new URLSearchParams(queryObj);

    fetch("search/resources" + "?" + qs.toString())
        .then(response => response.json())
        .then(data => {
            console.log(data);
            searchResults.value = data.results.hits.hits;
        }); 

    // self.updateRequest = $.ajax({
    //     type: "GET",
    //     url: arches.urls.search_results,
    //     data: queryObj,
    //     context: this,
    //     success: function(response) {
    //         _.each(this.sharedStateObject.searchResults, function(value, key, results) {
    //             if (key !== "timestamp") {
    //                 delete this.sharedStateObject.searchResults[key];
    //             }
    //         }, this);
    //         _.each(response, function(value, key, response) {
    //             if (key !== "timestamp") {
    //                 this.sharedStateObject.searchResults[key] = value;
    //             }
    //         }, this);
    //         this.sharedStateObject.searchResults.timestamp(response.timestamp);
    //         this.sharedStateObject.userIsReviewer(response.reviewer);
    //         this.sharedStateObject.userid(response.userid);
    //         this.sharedStateObject.total(response.total_results);
    //         this.sharedStateObject.hits(response.results.hits.hits.length);
    //         this.sharedStateObject.alert(false);
    //     },
    //     error: function(response, status, error) {
    //         const alert = new AlertViewModel("ep-alert-red", arches.translations.requestFailed.title, response.responseJSON?.message);
    //         if(self.updateRequest.statusText !== "abort"){
    //             this.alert(alert);
    //         }
    //         this.sharedStateObject.loading(false);
    //     },
    //     complete: function(request, status) {
    //         self.updateRequest = undefined;
    //         window.history.pushState({}, "", "?" + $.param(queryObj).split("+").join("%20"));
    //         this.sharedStateObject.loading(false);
    //     }
    // });
};

onMounted(() => {
    doQuery();
});


</script>

<template>
    <div class="container">
        <!-- Main Content Section -->
        <header>
            <SimpleSearchFilter style="flex-grow: 1;max-width: 800px;" :update-filter/>
            <div class="view-buttons">
                <Button :class="{ active: !showMap }" variant="outlined" label="terms" icon="pi pi-file"  icon-pos="top" @click="showMap = false" />
                <Button :class="{ active: showMap }" variant="outlined" label="map" icon="pi pi-map"  icon-pos="top" @click="showMap = true" />
            </div>  
        </header>
        
        <main>
            <section class="search-results-panel">
                <p class="result-count">342,112 Concepts</p>
                <div class="search-result-list">
                    <SearchResultItem v-for="searchResult in searchResults" :search-result :key="searchResult" />
                </div>
            </section>

            <MapView v-if="showMap" />
            
            <aside v-if="!showMap" >
                <h2>Search Facets</h2>
                <section class="facets">
                    <div class="facet-item selected">
                        <p>Reference Objects</p>
                        <p>Items in our reference collection, such as papers, paints, textiles, and other items</p>
                        <a href="#">click to unselect</a>
                    </div>
                    <div class="facet-item">
                        <p>Samples</p>
                        <p>Materials removed from works of art or other reference objects</p>
                        <a href="#">click to select</a>
                    </div>
                    <div class="facet-item">
                        <p>Building Materials</p>
                        <p>Construction materials and related objects</p>
                        <a href="#">click to select</a>
                    </div>
                </section>
            </aside>
            
        </main>
    </div>

    <Toast />
</template>

<style scoped>
:root {
    font-size: 16px;
}
.container {
    font-family: Arial, sans-serif;
    background-color: #f8f8f8;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
}
main {
    display: flex;
    flex-direction: row;
    height: 100vh;
}
header {
    font-size: 2rem;
    display: flex;
    border-bottom: 1px #ccc solid;
    padding: 5px;
}
.view-buttons {
    display: flex;
    gap: 5px;
    margin-left: 20px;
}
.search-results-panel {
    display: flex; 
    flex-direction: column; 
    flex-grow: 1; 
    margin: 20px;
    overflow-y: auto;
}
.search-result-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.result-count {
    font-size: 1.2rem;
    font-weight: bold;
    margin: 0px;
    margin-bottom: 15px;
}
aside {
    max-width: 25%;
    border-left: 1px #ccc solid;
}
.facets {
    padding: 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.facet-item {
    font-size: .7rem;
    padding: 16px;
    border: 1px solid #ddd;
    text-align: center;
    cursor: pointer;
    max-width: 11rem;
    min-height: 11rem;
}
.facet-item.selected {
    background-color: #f0f8ff;
    border-color: #007bff;
}
</style>

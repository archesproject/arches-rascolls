<script setup lang="ts">
import { ref, watch } from "vue";

import Toast from "primevue/toast";
import SimpleSearchFilter from "./components/SimpleSearchFilter.vue";   
import SearchResultItem from "./components/SearchResultItem.vue";

let query = getQueryObject();
let queryString = ref(JSON.stringify(query.value));
let searchResults = ref([]);

watch(queryString, (newValue, oldValue) => {
    doQuery();
});

function updateFilter(value: object) {
    console.log(value);
    const newQuery = { ...query, ...value };
    queryString.value = JSON.stringify(newQuery);
}

function getQueryObject(uri) {
    const url = new URL(uri || location.href);
    const params = new URLSearchParams(url.search);
    const obj = {};

    for (const [key, value] of params.entries()) {
        obj[key] = value;
    }

    return obj;
}

const doQuery = function() {
    // const queryObj = JSON.parse(this.queryString());
    // if (self.updateRequest) { self.updateRequest.abort(); }

    fetch("search/resources" + "?" + queryString.value)
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


</script>

<template>
    <div class="container">
        <!-- Main Content Section -->
        <main>
            <header>
                <h1>Site Search</h1>
            </header>
            
            <section>
                <SimpleSearchFilter :update-filter/>
            </section>
            
            <section class="search-controls">
                <p class="result-count">342,112 Concepts</p>
                <nav>
                    <label>
                        <select aria-label="Categories">
                            <option>Categories</option>
                        </select>
                    </label>
                    <label>
                        <select aria-label="Sort by">
                            <option>Sort by</option>
                        </select>
                    </label>
                </nav>
            </section>

            <SearchResultItem v-for="searchResult in searchResults" :search-result :key="searchResult" />

            <!-- Sample Results
            <article class="result">
                <h2>Stratford [Inhabited Place]</h2>
                <p class="breadcrumb">(North and Central America &gt; United States &gt; Missouri &gt; Greene)</p>
                <p class="scope-note">
                    <strong>Scope Note:</strong> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
                <p class="associated-concepts">
                    <strong>Associated Concepts:</strong> <a href="#">slotted spoon</a>
                </p>
            </article>

            <article class="result">
                <h2>strawberry jars</h2>
                <p class="breadcrumb">(Art and Architecture Thesaurus &gt; Objects Facet &gt; Furnishings and Equipment &gt; Containers &gt; horticultural containers)</p>
                <p class="scope-note">
                    <strong>Scope Note:</strong> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
                <p class="associated-concepts">
                    <strong>Associated Concepts:</strong> none
                </p>
            </article> -->

            <!-- Repeat Result Format as needed -->
        </main>

        <!-- Sidebar Section -->
        <aside>
            <h3>Search Tools</h3>
            <ul>
                <li><a href="#">Search Controlled Vocabularies</a></li>
                <li><a href="#">Search for People and Groups</a></li>
                <li><a href="#">Search for Places</a></li>
                <li><a href="#">Search for Periods</a></li>
                <li><a href="#">Export and use our authoritative datasets</a></li>
            </ul>
        </aside>
    </div>

    <Toast />
</template>

<style scoped>
:root {
    font-size: 16px;
}
.container {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f8f8;
    line-height: 1.6;
    display: flex;
    max-width: 75rem; /* approx 1200px */
    margin: 0 auto;
    padding: 1.25rem; /* 20px */
    gap: 1.25rem;
}
header h1 {
    font-size: 2rem;
    margin-bottom: 0.625rem;
}

.search-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.625rem;
}
.search-controls select {
    padding: 0.3125rem; /* 5px */
    font-size: 1rem;
}
.result-count {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1.25rem;
}
.result {
    background-color: #fff;
    padding: 0.9375rem; /* 15px */
    border: 1px solid #ddd;
    border-radius: 0.3125rem; /* 5px */
    margin-bottom: 0.9375rem;
}
.result h2 {
    margin: 0 0 0.625rem;
    font-size: 1.2rem;
}
.result .breadcrumb {
    color: #888;
    font-size: 0.9rem;
    margin-bottom: 0.625rem;
}
.result .scope-note {
    font-size: 0.9rem;
    color: #555;
    margin-bottom: 0.625rem;
}
.result .associated-concepts a {
    color: #1a73e8;
    text-decoration: none;
}
aside {
    flex: 1;
    background-color: #f1f1f1;
    padding: 20px;
    border-radius: 5px;
}
aside h3 {
    font-size: 1.2rem;
    margin-bottom: 0.625rem;
}
aside ul {
    list-style: none;
    padding: 0;
}
aside ul li {
    margin-bottom: 0.625rem;
}
aside ul li a {
    text-decoration: none;
    color: #1a73e8;
}
</style>

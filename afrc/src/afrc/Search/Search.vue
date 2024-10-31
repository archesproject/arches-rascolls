<script setup lang="ts">
import Toast from "primevue/toast";

</script>

<template>
    <div class="container">
        <!-- Main Content Section -->
        <main>
            <header>
                <h1>Site Search</h1>
            </header>
            
            <section class="search-bar">
                <input type="text" placeholder="Search for concepts..." aria-label="Search">
                <button type="submit">Search</button>
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

            <!-- Sample Results -->
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
            </article>

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
.search-bar {
    display: flex;
    margin-bottom: 1.25rem;
}
.search-bar input[type="text"] {
    flex: 1;
    padding: 0.625rem; /* 10px */
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 0.3125rem 0 0 0.3125rem; /* 5px */
}
.search-bar button {
    padding: 0.625rem 1.25rem; /* 10px 20px */
    font-size: 1rem;
    border: none;
    background-color: #ffcc33;
    color: #333;
    cursor: pointer;
    border-radius: 0 0.3125rem 0.3125rem 0;
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

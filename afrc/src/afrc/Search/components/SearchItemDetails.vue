<script setup lang="ts">
import { onMounted, inject, ref, watch } from "vue";
import { fetchResourceData } from "@/afrc/Search/api.ts";
import type { Ref } from "vue";
import Button from "primevue/button";
import Carousel from 'primevue/carousel';

const resultSelected = inject("resultSelected") as Ref<string>;
const resultsSelected = inject("resultsSelected") as Ref<string[]>;

let displayname = ref("")
let displaydescription = ref("")
let images = ref([])



onMounted(async () => {
    getData();
});

watch(resultSelected, () => {
    getData()
});

async function getData() {
    const resp = await fetchResourceData(resultSelected.value);
    displayname.value = resp.displayname;
    displaydescription.value = resp.displaydescription;
    images.value = [
        'http://www.minisimmonssurfboards.com/wp-content/uploads/2012/07/mini_simmons_round_tail.jpg',
        'https://www.minisimmonssurfboards.com/wp-content/uploads/2013/08/DOC-Mini-Simmons-1.jpg',
        'https://www.minisimmonssurfboards.com/wp-content/uploads/2013/06/20130606-222901.jpg',
        'https://www.surfboardsbygrantnewby.com/wp-content/uploads/2020/12/Traditional-Mini-Simmons.jpg',
        'https://i0.wp.com/www.minisimmonssurfboards.com/wp-content/uploads/2015/11/5_mandala_doubleRainbow_PinotNoir_1024x1024.jpg?resize=600%2C800',
        'https://3.bp.blogspot.com/-O0s9gHdDs-c/TW0i1DgLfBI/AAAAAAAAEMc/p3gwEQ9fziE/s1600/mini-simmons.jpg',
        ];
}

function clearResult() {
    resultSelected.value = "";
    resultsSelected.value = [];
}

</script>

<template>
    <div class="search-item-details">
        <div class="title">
            <div style='display:flex; flex-direction: column; padding: 3px'>
                <div>
                {{ displayname || "No name provided" }}
                </div>
                <div style="font-size: 0.7em; color: steelblue; font-style: italic; font-weight: 400;">
                    (Room 32, Row 2, Shelf 3)
                </div>
            </div>
            <div>
            <Button
                label="Close"
                severity="secondary"
                icon="pi pi-times-circle"
                icon-pos="top"
                text
                size="large"
                @click="clearResult()"
            />
            </div>
        </div>
        <div class="description">
            {{ displaydescription || "No description provided" }} <span>Sed ut perspiciatis, unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam eaque ipsa, quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt, explicabo. Nemo enim ipsam voluptatem, quia voluptas sit, aspernatur aut odit aut fugit</span>
        </div>
        <div class="images">
        <Carousel :value="images" :numVisible="2" :numScroll="1" containerClass="flex items-center">
        <template #item="image">
            <div class="border border-surface-200 dark:border-surface-700 rounded m-2  p-4">
                <div class="mb-4">
                    <div class="relative mx-auto">
                        <div style="padding: 3px">
                        <img :src="image.data" height="120px" width="120px" class="w-full rounded" />
                        </div>
                    </div>
                </div>
            </div>
        </template>
        </Carousel>
        </div>
        <div class="resource-details">
            <div class="value-header">Chemical Information</div>
            <div class="value-entry">Chemical (CAS) Number:<span class="resource-details-value">1309-36-0</span></div>
            <div class="value-entry">Chemical Formula:<span class="resource-details-value">FeS2</span></div>
            <div class="value-entry">Chemical Name:<span class="resource-details-value">Iron Disulfide</span></div>
            <div class="value-entry">Common Name:<span class="resource-details-value">Pyrite, Fool's Gold</span></div>
        </div>
        <div class="resource-details">
            <div class="value-header">Aquisition Information</div>
            <div class="value-entry">Acquired by:<span class="resource-details-value">Art Kaplan</span></div>
            <div class="value-entry">Acquired from:<span class="resource-details-value">Minerals-R-Us</span></div>
            <div class="value-entry">Acquired on:<span class="resource-details-value">Feb 18, 2001</span></div>
        </div>
        
    </div>
</template>

<style scoped>
    .search-item-details {
        display: flex;
        flex-direction: column;
        padding: 5px;
        border-right: #ddd solid 1px;
        border-left: solid #ddd 1px;
        width: 375px;
        height: 100%;
        background-color: #fff;
    }
    .title {
        display: flex;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
        justify-content: space-between;
        border-bottom: #ddd solid 1px;
    }
    .description {
        font-size: 1em;
        margin-bottom: 15px;
        padding: 10px;
    }
    .resource-details {
        padding: 10px;
    }
    .value-header {
        color: steelblue;
        font-size: 1.1em;
        font-weight: bold;
    }
    .value-entry {
        font-size: 1.0em;
        padding: 0px 3px;
    }
    .resource-details-value {
        color: steelblue;
        padding: 0px 3px;
    }
</style>
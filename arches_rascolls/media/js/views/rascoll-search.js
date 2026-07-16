import SearchPage from '@/arches_rascolls/Search/SearchPage.vue';
import { createVueApplication } from '@/arches_vue_components/application';

createVueApplication({ component: SearchPage }).then(vueApp => {
    vueApp.mount('#rascoll-search-container');
});
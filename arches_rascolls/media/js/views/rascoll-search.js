import SearchPage from '@/arches_rascolls/Search/SearchPage.vue';
import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

createVueApplication(SearchPage).then(vueApp => {
    vueApp.mount('#rascoll-search-container');
});
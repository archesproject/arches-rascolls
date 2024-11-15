import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

import Search from '@/afrc/Search/SearchPage.vue';

createVueApplication(Search).then(vueApp => {
    vueApp.mount('#search-mounting-point');
});

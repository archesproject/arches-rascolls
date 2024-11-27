import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

import Search from '@/afrc/Search/SearchPage.vue';

export function createAFRCApp() {
    const EditableReportPreset = definePreset(Aura, {
        components: {
            toast: {
                summary: { fontSize: '1.5rem' },
                detail: { fontSize: '1.25rem' },
            },
        },
    });
    
    const EditableReportTheme = {
        theme: {
            preset: EditableReportPreset,
        },
    };
    createVueApplication(Search, EditableReportTheme).then(vueApp => {
        vueApp.mount('#search-mounting-point');
    });
}
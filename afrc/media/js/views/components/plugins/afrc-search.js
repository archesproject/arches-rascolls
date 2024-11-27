import ko from 'knockout';
import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

import Search from '@/afrc/Search/SearchPage.vue';
import AFRCSEarchTemplate from 'templates/views/components/plugins/afrc-search.htm';

ko.components.register('afrc-search', {
    viewModel: function() {
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
    },
    template: AFRCSEarchTemplate,
});
import ko from 'knockout';
import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

import { definePreset } from '@primeuix/themes';
import { DEFAULT_THEME } from "@/arches/themes/default.ts";
import Search from '@/arches_rascolls/Search/SearchPage.vue';
import ArchesRascollsSearchTemplate from 'templates/views/components/plugins/arches-rascolls-search.htm';

export default ko.components.register('arches-rascolls-search', {
    viewModel: function() {
        const RascollsThemePreset = definePreset(DEFAULT_THEME, {
            components: {
                toast: {
                    summary: { fontSize: '1.5rem' },
                    detail: { fontSize: '1.25rem' },
                },
                autocomplete: {
                    colorScheme: {  
                        light: { 
                            option: {
                                group: {
                                    background: "lightgrey"
                                },
                            }
                        },  
                        dark: {  
                            option: {
                                group: {
                                    background: "lightgrey"
                                }
                            }
                        }
                    }
                }
            }
        });
        
        const EditableReportTheme = {
            theme: {
                preset: RascollsThemePreset, ...DEFAULT_THEME.theme,
            },
        };
        createVueApplication(Search, EditableReportTheme).then(vueApp => {
            vueApp.mount('#search-mounting-point');
        });
    },
    template: ArchesRascollsSearchTemplate,
});
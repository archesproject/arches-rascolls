import ko from 'knockout';
import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application';

import { DEFAULT_THEME } from "@/arches/themes/default.ts";
import GraphRelationViewer from '@/arches_rascolls/plugins/GraphRelationViewer.vue';
import GraphRelationViewerTemplate from 'templates/views/components/plugins/graph-relation-viewer.htm';

export default ko.components.register('graph-relation-viewer', {
    viewModel: function() {
        createVueApplication(GraphRelationViewer, DEFAULT_THEME).then(vueApp => {
            vueApp.mount('#graph-relation-viewer-mounting-point');
        });
    },
    template: GraphRelationViewerTemplate,
});

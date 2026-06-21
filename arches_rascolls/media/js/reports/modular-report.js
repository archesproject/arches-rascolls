import ko from 'knockout';
import ModularReport from '@/arches_modular_reports/ModularReport/ModularReport.vue';
import createVueApplication from 'utils/create-vue-application';
import ModularReportTemplate from 'templates/views/report-templates/modular-report.htm';
import { fetchGraphSlugFromId } from '@/arches_modular_reports/ModularReport/api.ts';
import ModularReportTheme from '@/arches_rascolls/report_themes/rascolls_theme.ts';


// Shadows arches_modular_reports/media/js/reports/modular-report.js to apply
// the RaSColls report theme (the package does not yet support dynamic theme
// imports from config).
ko.components.register('modular-report', {
    viewModel: async function(params) {

        let graphSlug = params.report.graph?.slug || params.report.report_json.graph_slug;
        const resourceInstanceId = params.report.report_json.resourceinstanceid;
        const reportConfigSlug = params.report.report_json.report_config_slug;

        if (!graphSlug) {
            // fetch graph slug from graph id this can happen when viewing the
            // report from the "details" section of search
            const graphId = params.report.graph?.id || params.report.report_json.graph_id;
            const data = await fetchGraphSlugFromId(graphId);
            graphSlug = data.graph_slug;
        }

        createVueApplication(ModularReport, ModularReportTheme, { graphSlug, resourceInstanceId, reportConfigSlug }).then(vueApp => {
            // RaSColls reports are light-only: the legacy Arches chrome does not
            // support dark mode, so a report that flips to dark (when the browser
            // reports prefers-color-scheme: dark, e.g. Firefox's "Website
            // appearance" setting) clashes with the surrounding light chrome.
            // create-vue-application adds .arches-dark to <html> based on that
            // browser preference; strip it so the report always renders light.
            // Remove this once the project commits to a full dark-mode treatment.
            document.documentElement.classList.remove('arches-dark');

            // handles the Graph Designer case of multiple mounting points on the same page
            const mountingPoints = document.querySelectorAll('.modular-report-mounting-point');
            const mountingPoint = mountingPoints[mountingPoints.length - 1];

            // handles the Resource Editor case of navigating from report doesn't unmount the previous app
            if (window.archesModularReportVueApp) {
                window.archesModularReportVueApp.unmount();
            }
            window.archesModularReportVueApp = vueApp;

            vueApp.mount(mountingPoint);
        });
    },
    template: ModularReportTemplate,
});

define([
    'knockout',
    'views/afrc-search',
    'templates/views/components/plugins/afrc-search-plugin.htm',
], function(ko, AFRCSEarchComponent, AFRCSEarchTemplate) {
    return ko.components.register('afrc-search-plugin', {
        viewModel: function() {
            AFRCSEarchComponent.createAFRCApp();
        },
        template: AFRCSEarchTemplate,
    });
});
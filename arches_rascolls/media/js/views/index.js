import ko from 'knockout';
import arches from 'arches';
import 'views/components/language-switcher';

/**
 * Bindings for the splash page.
 *
 * These must be applied from inside the bundle: the `ko` webpack resolves is a
 * separate instance from the `window.ko` created by the knockout script tag in
 * index.htm, and components (language-switcher) are registered against this one.
 */
const IndexViewModel = function() {
    this.translations = arches.translations;
};

$(document).ready(function() {
    ko.applyBindings(new IndexViewModel());
});

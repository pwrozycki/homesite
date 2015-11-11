(function () {
    'use strict';

    angular
        .module('homeGallery')
        .run(runBlock);

    /** @ngInject */
    function runBlock($log) {
        $log.debug('runBlock end');
    }

})();

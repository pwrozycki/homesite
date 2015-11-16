(function () {
    'use strict';

    angular
        .module('angular')
        .run(runSession);

    /* @ngInject */
    function runSession(sessionService) {
        sessionService._checkSession();
    }

})();

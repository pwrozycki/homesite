(function () {
    'use strict';

    angular
        .module('angular')
        .factory('slideshowService', slideshowService);

    /* @ngInject */
    function slideshowService() {
        var paused = true;

        var service = {
            setPaused: setPaused,
            isPaused: isPaused
        };

        return service;

        ////////////////

        function setPaused(newPaused) {
            paused = newPaused;
        }

        function isPaused() {
            return paused;
        }
    }

})();


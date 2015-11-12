(function () {
    'use strict';

    angular
        .module('angular')
        .controller('PreviewController', PreviewController);

    /* @ngInject */
    function PreviewController(imagePromise) {
        var vm = this;
        vm.title = 'PreviewController';
        vm.image = imagePromise;

        activate();

        ////////////////

        function activate() {

        }
    }

})();


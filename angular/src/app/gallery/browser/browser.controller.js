(function () {
    'use strict';

    angular
        .module('angular')
        .controller('BrowserController', BrowserController);

    /* @ngInject */
    function BrowserController(directoryPromise) {
        var vm = this;
        vm.directory = directoryPromise;
    }
})();
(function () {
    'use strict';

    angular
        .module('angular')
        .controller('DirectoryController', DirectoryController);

    /* @ngInject */
    function DirectoryController(directoryObj) {
        var vm = this;
        vm.directory = directoryObj.results[0];
    }
})();
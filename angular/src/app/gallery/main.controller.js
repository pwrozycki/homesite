(function () {
    'use strict';

    angular
        .module('angular')
        .controller('MainController', MainController);

    /* @ngInject */
    function MainController() {
        var vm = this;
        vm.title = 'MainController';

        activate();

        ////////////////

        function activate() {
        }
    }

})();


(function () {
    'use strict';

    angular
        .module('angular')
        .controller('MainController', MainController);

    /* @ngInject */
    function MainController(titleService) {
        var vm = this;
        vm.title = 'MainController';

        activate();

        ////////////////

        function activate() {
            titleService.setTitleForState('homeGallery');
        }
    }

})();


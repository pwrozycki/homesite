(function () {
    'use strict';

    angular
        .module('angular')
        .directive('directoryPath', directoryPath);

    /* @ngInject */
    function directoryPath(pathsService) {
        var directive = {
            bindToController: true,
            controller: DirectoryPathController,
            controllerAs: 'vm',
            templateUrl: "app/gallery/browser/directoryPath.directive.html",
            scope: {
                path: '='
            }
        };

        return directive;

        //////////

        function DirectoryPathController() {
            var vm = this;
            vm.parentPaths = [""].concat(pathsService.parentPaths(vm.path));
        }
    }

})();
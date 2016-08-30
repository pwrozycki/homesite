(function () {
    'use strict';

    angular
        .module('angular')
        .directive('directoryLink', directoryLink);

    /* @ngInject */
    function directoryLink(pathsService, _) {
        var directive = {
            bindToController: true,
            controller: DirectoryLinkController,
            controllerAs: 'vm',
            templateUrl: "app/gallery/browser/directoryLink.directive.html",
            scope: {
                path: '=',
                showIcon: '&',
                name: '='
            }
        };

        return directive;

        //////////

        /* @ngInject */
        function DirectoryLinkController(pathsService) {
            var vm = this;

            vm.displayName = vm.name ? vm.name : pathsService.basename(vm.path);
            vm.mangledPath = pathsService.escapeSlashes(vm.path);

            if (_.isUndefined(vm.showIcon)) {
                vm.showIcon = true;
            }
        }
    }
})();

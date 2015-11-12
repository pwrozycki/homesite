(function () {
    'use strict';

    angular
        .module('angular')
        .directive('directoryPath', directoryPath);

    /* @ngInject */
    function directoryPath(pathsService) {
        var directive = {
            templateUrl: "app/gallery/directives/directoryPath.directive.html",
            scope: {
                path: '='
            },
            link: link
        };

        return directive;

        //////////

        function link(scope) {
            scope.parentPaths = [""].concat(pathsService.parentPaths(scope.path));
        }
    }

})();
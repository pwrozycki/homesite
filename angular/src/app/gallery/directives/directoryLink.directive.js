(function () {
    'use strict';

    angular
        .module('angular')
        .directive('directoryLink', directoryLink);

    /* @ngInject */
    function directoryLink(pathsService, _) {
        var directive = {
            templateUrl: "app/gallery/directives/directoryLink.directive.html",
            scope: {
                path: '=',
                showIcon: '=',
                name: '='
            },
            link: link
        };

        return directive;

        //////////

        function link(scope) {
            scope.displyName = scope.name ? scope.name : pathsService.basename(scope.path);

            if (_.isUndefined(scope.showIcon)) {
                scope.showIcon = true;
            }
        }
    }
})();
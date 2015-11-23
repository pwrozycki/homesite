(function () {
    'use strict';

    angular
        .module('angular')
        .directive('fullscreenOnDblclick', fullscreenOnDblclick);

    /* @ngInject */
    function fullscreenOnDblclick() {
        var directive = {
            link: link,
            restrict: 'A',
            scope: {}
        };

        return directive;

        function link(scope, element) {
            element.on('dblclick', requestFullScreen);

            scope.$on('$destroy', function() {
                element.off('dblclick', requestFullScreen);
            });

            function requestFullScreen() {
                var el = element[0];
                if (el.requestFullscreen) {
                    el.requestFullscreen();
                } else if (el.mozRequestFullScreen) {
                    el.mozRequestFullScreen();
                } else if (el.webkitRequestFullscreen) {
                    el.webkitRequestFullscreen();
                }
            }
        }


    }
})();


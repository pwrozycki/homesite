(function () {
    'use strict';

    angular
        .module('angular')
        .directive('downloadButtons', downloadButtons);

    /* @ngInject */
    function downloadButtons() {
        var directive = {
            templateUrl: 'app/gallery/browser/downloadButtons.directive.html',
            bindToController: true,
            controller: DownloadButtonsDirective,
            controllerAs: 'vm',
            scope: {
                image: '='
            }
        };
        return directive;
    }

    /* @ngInject */
    function DownloadButtonsDirective() {

    }

})();


(function () {
    'use strict';

    angular
        .module('angular')
        .controller('BrowserController', BrowserController);

    /* @ngInject */
    function BrowserController(directoryPromise, $rootScope, $window, $scope, $timeout) {
        var vm = this;
        vm.directory = directoryPromise;

        $scope.$on('$stateChangeSuccess', scrollToImageOnPreviewExit);

        function scrollToImageOnPreviewExit(event, toState, toParams, fromState, fromParams) {
            var returnFromPreview = toState.name === 'main.browser' && fromState.name === 'main.browser.preview';
            if (returnFromPreview) {
                $timeout(function () {
                    scrollToImage(fromParams.imageName)
                });
            }
        }

        function scrollToImage(imageName) {
            var jqImage = angular.element('img[data-name="' + imageName + '"]');
            if (jqImage.length) {
                var scrollTop = jqImage.offset().top + jqImage.height() / 2 - $window.innerHeight / 2;
                angular.element("body").animate({scrollTop: scrollTop}, 0);
            }
        }
    }
})();
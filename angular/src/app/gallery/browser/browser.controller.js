(function () {
    'use strict';

    angular
        .module('angular')
        .controller('BrowserController', BrowserController);

    /* @ngInject */
    function BrowserController(directoryPromise, $window, $scope, $timeout, titleService) {
        var vm = this;
        vm.directory = directoryPromise;

        activate();

        ////////////////

        function activate() {
            $scope.$on('$stateChangeSuccess', scrollToImageOnPreviewExit);
            titleService.setTitleForState('homeGallery - ' + (vm.directory.path ? vm.directory.path : "ROOT"));
        }

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
                angular.element("body").scrollTop(scrollTop);
            }
        }
    }
})();
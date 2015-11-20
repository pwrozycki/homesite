(function () {
    'use strict';

    angular
        .module('angular')
        .controller('PreviewController', PreviewController);

    /* @ngInject */
    function PreviewController(directoryPromise, imagePromise, preloaderService, $scope, $state, _) {
        var vm = this;
        vm.title = 'PreviewController';
        vm.image = imagePromise;
        vm.previewPath = null;
        vm.previousImage = previousImage;
        vm.nextImage = nextImage;

        activate();

        ////////////////

        function activate() {
            createPreloader();
        }

        function createPreloader() {
            var cancelPreload = preloaderService.preload([vm.image._previewPath], function() {
                vm.previewPath = vm.image._previewPath;
            });

            $scope.$on('$destroy', cancelPreload);
        }

        function nextImage() {
            switchToImage(1);
        }

        function previousImage() {
            switchToImage(-1);
        }

        function switchToImage(sign) {
            var currentIndex = getCurrentImageIndex();

            var newIndex = currentIndex + sign;

            if (newIndex >= 0 && newIndex < directoryPromise._images.length) {
                var newName = directoryPromise._images[newIndex]._name;
                $state.go('^.preview', {imageName: newName})
            }
        }

        function getCurrentImageIndex() {
            return _.findIndex(directoryPromise._images, function (el) {
                return el._name === vm.image._name;
            });
        }
    }

})();


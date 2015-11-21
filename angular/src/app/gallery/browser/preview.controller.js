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
            // preload current image
            var cancelPreload = preloaderService.preload([vm.image._previewPath], onCurrentImagePreload);
            $scope.$on('$destroy', cancelPreload);

            function onCurrentImagePreload() {
                // when done - set previewPath accordingly
                vm.previewPath = vm.image._previewPath;

                // and setup preload for neighbouring images
                var cancelPreloadNeighbours = preloaderService.preload(neighbouringImageUrls());
                $scope.$on('$destroy', cancelPreloadNeighbours);
            }
        }

        function neighbouringImageUrls() {
            var currentImageIndex = getCurrentImageIndex();
            var images = directoryPromise._images;

            var urls = [];
            _.forEach([1, 2], function(distance) {
                _.forEach([-1, 1], function(sign) {
                    var index = distance * sign + currentImageIndex;
                    if (index >= 0 && index < images.length) {
                        urls.push(images[index]._previewPath);
                    }
                })
            });

            return urls;
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


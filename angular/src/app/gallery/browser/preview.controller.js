(function () {
    'use strict';

    angular
        .module('angular')
        .controller('PreviewController', PreviewController);

    /* @ngInject */
    function PreviewController(directoryPromise, imagePromise, fileService, preloaderService, $scope, $state, _) {
        var vm = this;
        vm.title = 'PreviewController';
        vm.directory = directoryPromise;
        vm.image = imagePromise;

        vm.onImageMove = onImageMove;

        vm.previousImage = previousImage;
        vm.nextImage = nextImage;

        activate();

        ////////////////

        function activate() {
            createPreloader();
            setKeyBindings();
        }

        function createPreloader() {
            var cancelPreloadNeighbours = preloaderService.preload(neighbouringImageUrls());
            $scope.$on('$destroy', cancelPreloadNeighbours);
        }
        
        function onImageMove() {
            var currentImageIndex = getCurrentImageIndex();
            if (currentImageIndex + 1 < directoryPromise._images.length) {
                nextImage();
            } else if (currentImageIndex > 0) {
                previousImage();
            } else {
                $state.go('^');
            }
        }

        function neighbouringImageUrls() {
            var images = directoryPromise._images;
            var currentImageIndex = getCurrentImageIndex();

            var urls = [];
            _.forEach([1, 2], function (distance) {
                _.forEach([-1, 1], function (sign) {
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
            return _.findIndex(directoryPromise._images, { path: vm.image.path });
        }

        function setKeyBindings() {
            var jqBody = angular.element('body');

            jqBody.on('keydown', handleKeydown);

            $scope.$on('$destroy', function () {
                jqBody.off('keydown', handleKeydown)
            });

            function handleKeydown(event) {
                // left arrow
                if (event.which === 37) {
                    previousImage();
                    // right arrow
                } else if (event.which === 39) {
                    nextImage();
                    // up arrow or escape key
                } else if (event.which === 38 || event.which === 27) {
                    $state.go('^');
                    // delete key
                } else if (event.which === 46) {
                    //var previewImage = self.get('controller.model');
                    //self.get('controller').send('removeFile', previewImage);
                }
            }
        }
    }

})();


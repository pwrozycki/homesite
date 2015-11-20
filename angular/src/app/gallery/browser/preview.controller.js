(function () {
    'use strict';

    angular
        .module('angular')
        .controller('PreviewController', PreviewController);

    /* @ngInject */
    function PreviewController(directoryPromise, imagePromise, $state, _) {
        var vm = this;
        vm.title = 'PreviewController';
        vm.image = imagePromise;
        vm.previousImage = previousImage;
        vm.nextImage = nextImage;

        activate();

        ////////////////

        function activate() {

        }

        function nextImage() {
            switchToImage(1);
        }

        function previousImage() {
            switchToImage(-1);
        }

        function switchToImage(sign) {
            var currentIndex = _.findIndex(directoryPromise._images, function (el) {
                return el._name === vm.image._name;
            });

            var newIndex = currentIndex + sign;

            if (newIndex >= 0 && newIndex < directoryPromise._images.length) {
                var newName = directoryPromise._images[newIndex]._name;
                $state.go('^.preview', {imageName: newName})
            }
        }
    }

})();


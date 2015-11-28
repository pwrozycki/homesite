(function () {
    'use strict';

    angular
        .module('angular')
        .directive('imageThumbnail', imageThumbnail);

    /* @ngInject */
    function imageThumbnail() {
        var directive = {
            bindToController: true,
            controllerAs: 'vm',
            controller: ImageThumbnailController,
            templateUrl: 'app/gallery/browser/imageThumbnail.directive.html',
            scope: {
                image: '=',
                directory: '=',
                height: '='
            }
        };

        return directive;
    }

    /* @ngInject */
    function ImageThumbnailController($state) {
        var vm = this;

        vm.thumbnailPath = null;
        vm.width = vm.height * vm.image.aspect_ratio;
        vm.onShow = show;

        function show() {
            if ($state.is('main.browser')) {
                vm.thumbnailPath = vm.image._thumbnailPath;
            }
        }
    }
})();


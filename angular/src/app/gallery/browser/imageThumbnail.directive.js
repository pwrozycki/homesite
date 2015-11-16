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
                height: '='
            }
        };

        return directive;
    }

    /* @ngInject */
    function ImageThumbnailController(pathsService, collectionPathsService, $scope) {
        var vm = this;

        var image = vm.image;

        image._name = pathsService.basename(image.path);
        image._height = vm.height;
        image._width = image.aspect_ratio * vm.height;

        vm.onShow = function () {
            if (!image._thumbnailPath) {
                image._thumbnailPath = collectionPathsService.thumbnailPath(image.path, image.timestamp);
            }
        };
    }
})();


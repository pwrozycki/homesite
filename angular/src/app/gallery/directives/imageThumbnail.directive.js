(function () {
    'use strict';

    angular
        .module('homeGallery')
        .directive('imageThumbnail', imageThumbnail);

    function imageThumbnail(galleryService, pathsService) {
        var directive = {
            scope: {image: ""},
            templateUrl: "",
            link: link
        };

        return directive;

        /////////

        function link(scope) {
            var collectionInfo = galleryService.getCollectionInfo();

            scope.pathWithTimestamp = scope.image.path + "_" + scope.image.timestamp + "_"

            scope.thumbnailPath = pathsService.join([collectionInfo.thumbnails_root, scope.image.path])
        }
    }
})();

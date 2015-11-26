(function () {
    'use strict';

    angular
        .module('angular')
        .directive('trashButton', trashButton);

    /* @ngInject */
    function trashButton() {
        var directive = {
            bindToController: true,
            controller: TrashButtonController,
            controllerAs: 'vm',
            templateUrl: 'app/gallery/browser/trashButton.directive.html',
            scope: {
                image: '=',
                directory: '=',
                onMove: '&'
            }
        };
        return directive;
    }

    /* @ngInject */
    function TrashButtonController(fileService, _) {
        var vm = this;

        vm.isImageInTrash = fileService.isImageInTrash(vm.image);
        vm.trashImage = trashImage;
        vm.untrashImage = untrashImage;

        function untrashImage() {
            return moveImage(fileService.moveFromTrash);
        }

        function trashImage() {
            return moveImage(fileService.moveToTrash);
        }

        function moveImage(operation) {
            if (vm.image._dirty) {
                return;
            }

            vm.image._dirty = true;

            operation(vm.image).then(function () {
                if (vm.onMove) {
                    vm.onMove();
                }

                vm.image.dirty = false;

                _.remove(vm.directory._images, {path: vm.image.path});
            });
        }
    }

})();


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
    function TrashButtonController(fileService, collectionPathsService, notificationsService, _) {
        var vm = this;

        vm.isImageInTrash = fileService.isImageInTrash(vm.image);
        vm.trashImage = trashImage;
        vm.untrashImage = untrashImage;

        function untrashImage() {
            return moveImage(fileService.moveFromTrash);
        }

        function trashImage() {
            return moveImage(fileService.moveToTrash).then(function() {
                var template = 'app/gallery/browser/trashButtonNotification.html';
                var notificationScope = {
                    vm: {
                        image: vm.image,
                        directory: vm.directory,
                        undoAction: undoAction
                    }
                };
                notificationsService.addNotification(template, notificationScope);
            });
        }

        function undoAction(undoVm) {
            var directory = undoVm.directory;
            var imageInTrash = _.clone(undoVm.image);

            undoVm.dirty = true;

            imageInTrash.path = collectionPathsService.pathInTrash(imageInTrash.path);

            fileService.moveFromTrash(imageInTrash).then(function() {
                undoVm.reverted = true;

                var insertionPoint = _.sortedIndex(directory._images, undoVm.image, 'path');
                directory._images.splice(insertionPoint, 0, undoVm.image);
            });

        }

        function moveImage(operation) {
            if (vm.dirty) {
                return;
            }

            vm.dirty = true;

            return operation(vm.image).then(function () {
                if (vm.onMove) {
                    vm.onMove();
                }

                _.remove(vm.directory._images, {path: vm.image.path});
            });
        }
    }

})();


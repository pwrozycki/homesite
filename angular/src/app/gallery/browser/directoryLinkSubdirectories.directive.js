(function () {
    'use strict';

    angular
        .module('angular')
        .directive('directoryLinkSubdirectories', directoryLinkSubdirectories);

    /* @ngInject */
    function directoryLinkSubdirectories($timeout, recursionHelperService) {
        var directive = {
            bindToController: true,
            controller: DirectoryLinkSubdirectoriesController,
            controllerAs: 'vm',
            templateUrl: "app/gallery/browser/directoryLinkSubdirectories.directive.html",
            scope: {
                path: '='
            },
            compile: function(element) {
                return recursionHelperService.compile(element, link);
            }
        };

        return directive;

        function link(scope, element, attrs, controller) {
            var jqParentDirectoryLink = element.closest("directory-link");
            var showTimeout = null;

            jqParentDirectoryLink.on('mouseenter', directoryLinkEnter);
            jqParentDirectoryLink.on('mouseleave', directoryLinkLeave);

            scope.$on('$destroy', function() {
                jqParentDirectoryLink.off('mouseenter', directoryLinkEnter);
                jqParentDirectoryLink.off('mouseleave', directoryLinkLeave);
                if (showTimeout) {
                    $timeout.cancel(showTimeout);
                }
            });

            function directoryLinkEnter() {
                showTimeout = $timeout(function() {
                    controller.loadSubdirectories();
                }, 1000);
            }

            function directoryLinkLeave() {
                if (showTimeout) {
                    $timeout.cancel(showTimeout);
                }
                controller.tearDown();
            }

        }
    }

    /* @ngInject */
    function DirectoryLinkSubdirectoriesController($element, directoryService) {
        var vm = this;

        vm.down = true;

        vm.loadSubdirectories = loadSubdirectories;
        vm.tearDown = tearDown;

        function loadSubdirectories() {
            vm.down = false;
            directoryService.getDirectory(vm.path).then(onDirectoryLoad);
        }

        function onDirectoryLoad(directory) {
            vm.directory = directory;
            if (vm.directory.subdirectories.length) {
                $element.show();
            }
        }

        function tearDown() {
            vm.directory = null;
            vm.down = true;
            $element.hide();
        }
    }

})();


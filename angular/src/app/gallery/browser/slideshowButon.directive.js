(function () {
    'use strict';

    angular
        .module('angular')
        .directive('slideshowButton', slideshowButton);


    /* @ngInject */
    function slideshowButton() {
        var directive = {
            bindToController: true,
            controller: SlideShowButtonController,
            controllerAs: 'vm',
            templateUrl: 'app/gallery/browser/slideshowButton.directive.html',
            scope: {
                next: '&onNext'
            }
        };
        return directive;
    }

    /* @ngInject */
    function SlideShowButtonController($timeout, slideshowService, $scope) {
        var vm = this;

        vm.play = play;
        vm.pause = pause;
        vm.timeout = null;
        vm.isPaused = slideshowService.isPaused;

        activate();

        function activate() {
            $scope.$on('$stateChangeStart', pauseOnExitPreview);

            if (!vm.isPaused()) {
                play();
            }
        }

        function pauseOnExitPreview(event, toState) {
            if (toState.name !== 'main.browser.preview') {
                pause();
            }
        }

        function play() {
            slideshowService.setPaused(false);
            vm.timeout = $timeout(function() {
                vm.next();
            }, 3000);
        }

        function pause() {
            slideshowService.setPaused(true);
            if (vm.timeout) {
                $timeout.cancel(vm.timeout);
            }
            vm.timeout = null;
        }
    }

})();


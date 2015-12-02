(function () {
    'use strict';

    angular
        .module('angular')
        .directive('authBox', authBox);

    /* @ngInject */
    function authBox() {
        var directive = {
            bindToController: true,
            controller: AuthBoxController,
            controllerAs: 'vm',
            templateUrl: 'app/components/auth/authBox.directive.html',
            scope: {}
        };

        return directive;
    }

    /* @ngInject */
    function AuthBoxController(sessionService) {
        var vm = this;

        vm.user = {};
        vm.isAuthenticated = sessionService.isAuthenticated;
        vm.getUsername = sessionService.getUsername;
        vm.login = login;
        vm.logout = logout;

        activate();

        ////////////////

        function activate() {
        }

        function login() {
            sessionService.login(vm.user);
        }

        function logout() {
            sessionService.logout();
        }
    }
})();

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
        vm.login = login;
        vm.logout = logout;

        activate();

        ////////////////

        function activate() {
            setLoggedUser();
        }

        function login() {
            sessionService.login(vm.user).then(setLoggedUser);
        }

        function logout() {
            sessionService.logout().then(function () {
                delete vm.user.login;
                delete vm.user.password;
            });
        }

        function setLoggedUser() {
            if (sessionService.isAuthenticated()) {
                vm.user.login = sessionService.getUsername();
            } else {
                delete vm.user.login;
            }
            delete vm.user.password;
        }
    }
})();

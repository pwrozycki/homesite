(function () {
    'use strict';

    angular
        .module('angular')
        .directive('authBox', authBox);

    /* @ngInject */
    function authBox(sessionService) {
        var directive = {
            templateUrl: 'app/components/auth/authBox.directive.html',
            scope: {},
            link: link
        };

        return directive;

        //////////

        function link(scope) {
            scope.user = {};
            scope.isAuthenticated = sessionService.isAuthenticated;

            setLoggedUser();

            scope.login = function () {
                sessionService.login(scope.user).then(setLoggedUser);
            };

            scope.logout = function () {
                sessionService.logout().then(function () {
                    delete scope.user.login;
                    delete scope.user.password;
                });
            };

            function setLoggedUser() {
                if (sessionService.isAuthenticated()) {
                    scope.user.login = sessionService.getUsername();
                } else {
                    delete scope.user.login;
                }
                delete scope.user.password;
            }
        }
    }
})();

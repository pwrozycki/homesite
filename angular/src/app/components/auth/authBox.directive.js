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
            sessionService.checkSession().then(setLoggedUser);

            scope.user = {};

            scope.login = function () {
                sessionService.login(scope.user).then(setLoggedUser);
            };

            scope.logout = function () {
                sessionService.logout().then(function () {
                    delete scope.loggedUser;
                    delete scope.user.login;
                    delete scope.user.password;
                });
            };

            scope.isAuthenticated = function () {
                return !!scope.loggedUser;
            };

            function setLoggedUser(user) {
                scope.loggedUser = user;
                scope.user.login = user.username;
                delete scope.user.password;
            }
        }
    }
})();

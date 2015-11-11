(function () {
    'use strict';

    angular
        .module('homeGallery')
        .directive('authBox', authBox);

    /* @ngInject */
    function authBox(authService) {
        var directive = {
            templateUrl: 'app/gallery/directives/authBox.directive.html',
            scope: {},
            link: link
        };

        return directive;

        //////////

        function link(scope) {
            authService.checkSession().then(setLoggedUser);

            scope.user = {};

            scope.login = function () {
                authService.login(scope.user).then(setLoggedUser);
            };

            scope.logout = function () {
                authService.logout().then(function () {
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

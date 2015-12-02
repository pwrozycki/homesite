(function () {
    'use strict';

    angular
        .module('angular')
        .factory('sessionService', sessionService);

    /* @ngInject */
    function sessionService(Restangular, $q, $rootScope, $timeout, $window) {
        var Session = Restangular.all('session');
        var User = Restangular.all('users');

        var session = {
            username: null
        };

        var ready = $q.defer();

        var service = {
            login: login,
            logout: logout,
            getUsername: getUsername,
            isAuthenticated: isAuthenticated,

            ready: ready.promise,
            init: init
        };

        return service;

        //////////

        function login(user) {
            return checkSessionPromise(
                Session.post({
                    username: user.login,
                    password: user.password
                }));
        }

        function logout() {
            return Session.remove(1).then(function () {
                onSessionLogout();
                return session;
            });
        }

        function isAuthenticated() {
            return !!session.username;
        }

        function getUsername() {
            return session.username;
        }

        function init() {
            return checkSessionPromise(Session.get("")).then(function () {
                ready.resolve();
                periodicallyCheckSession();
            });
        }

        function onSessionLogin(username) {
            session.username = username;
            $window.localStorage.username = angular.toJson(username);
            $rootScope.$broadcast('session:login', session);
        }

        function onSessionLogout() {
            session.username = null;
            $window.localStorage.username = null;
            $rootScope.$broadcast('session:logout');
        }

        function periodicallyCheckSession() {
            var username = angular.fromJson($window.localStorage.username);
            if (username !== session.username) {
                if (username) {
                    onSessionLogin(username);
                } else {
                    onSessionLogout();
                }
            }
            $timeout(periodicallyCheckSession, 1000);
        }

        function checkSessionPromise(sessionPromise) {
            // check session promise
            return sessionPromise.then(function (session) {
                return $q(function (resolve, reject) {
                    if (!session.user_id) {
                        reject();
                    } else {
                        resolve(session.user_id);
                    }
                });
            }).then(function (userId) {
                return User.get(userId);
            }).then(
                function (user) {
                    onSessionLogin(user.username);
                },
                onSessionLogout
            );
        }
    }
})();
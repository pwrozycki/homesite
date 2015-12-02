(function () {
    'use strict';

    angular
        .module('angular')
        .factory('sessionService', sessionService);

    /* @ngInject */
    function sessionService(Restangular, $q, $rootScope) {
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
                session.username = null;
                $rootScope.$broadcast('session:logout');
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
            });
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
            }).then(function (user) {
                session.username = user.username;
                $rootScope.$broadcast('session:login', session);
                return session;
            }).catch(function () {
                session.username = null;
            });
        }
    }
})();
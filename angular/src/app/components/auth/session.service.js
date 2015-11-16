(function () {
    'use strict';

    angular
        .module('angular')
        .factory('sessionService', sessionService);

    /* @ngInject */
    function sessionService(Restangular, $q) {
        var Session = Restangular.all('session');
        var User = Restangular.all('users');

        var session = {
            username: null
        };

        var service = {
            login: login,
            logout: logout,
            getUsername: getUsername,
            isAuthenticated: isAuthenticated,

            _checkSession: checkSession
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
            return Session.remove(1).then(function() {
                session.username = null;
                return session;
            });
        }

        function isAuthenticated() {
            return !!session.username;
        }

        function getUsername() {
            return session.username;
        }

        function checkSession() {
            return checkSessionPromise(Session.get(""));
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
                return session;
            }).catch(function() {
                session.username = null;
            });
        }
    }
})();
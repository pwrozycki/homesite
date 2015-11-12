(function () {
    'use strict';

    angular
        .module('angular')
        .factory('sessionService', sessionService);

    /* @ngInject */
    function sessionService(Restangular, $q) {
        var Session = Restangular.all('session');
        var User = Restangular.all('users');

        var service = {
            login: login,
            logout: logout,
            checkSession: checkSession
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
            return Session.remove(1);
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
            });
        }
    }
})();
(function () {
    'use strict';

    angular
        .module('angular')
        .factory('notificationsService', notificationsService);

    /* @ngInject */
    function notificationsService($rootScope, $templateCache, $http) {
        var service = {
            addNotification: addNotification
        };

        return service;

        ////////////////

        function addNotification(templatePath, scope) {
            var template = $templateCache.get(templatePath);

            if (template) {
                // in production environment: template will always be available in $templateCache
                notifyContainerDirective(template, scope);
            } else {
                // in development environment: fetch template from server
                // ($templateCache isn't injected to index.html)
                $http.get(templatePath).then(function (response) {
                    notifyContainerDirective(response.data, scope);
                });
            }
        }

        function notifyContainerDirective(template, scope) {
            $rootScope.$broadcast("notifications:add", template, scope);
        }
    }

})();


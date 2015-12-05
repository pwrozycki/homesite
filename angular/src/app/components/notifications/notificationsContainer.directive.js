(function () {
    'use strict';

    angular
        .module('angular')
        .directive('notificationsContainer', notificationsContainer);

    /* @ngInject */
    function notificationsContainer($compile, $timeout, _) {
        var directive = {
            link: link,
            scope: {}
        };

        return directive;

        function link(scope, element) {
            var notificationElements = [];

            scope.$on('notifications:add', addNotification);

            function addNotification(event, template, templateScope) {
                // create new scope
                var newScope = scope.$new(true);
                _.extend(newScope, templateScope);

                // compile template
                var compiledTemplate = $compile(wrapTemplate(template));

                // apply scope and attach to DOM
                compiledTemplate(newScope, function(compiledElement) {
                    addNotificationElement(compiledElement);

                    // after predefined timeout remove notification
                    $timeout(removeNotificationElement, 5000, true, {
                        element: compiledElement,
                        scope: newScope
                    });
                });
            }

            function addNotificationElement(compiledElement) {
                element.append(compiledElement);
                notificationElements.push(compiledElement);
                calculateNewPositions();
            }

            function removeNotificationElement(notificationData) {
                notificationData.element.remove();
                notificationData.scope.$destroy();
                notificationElements.shift();
                calculateNewPositions();
            }

            function wrapTemplate(template) {
                return "<notification-element>" + template + "</notification-element>";
            }

            function calculateNewPositions() {
                var bottom = 0;

                notificationElements.forEach(function(element, index) {
                    element.css('bottom', bottom);
                    bottom += element.outerHeight(true);
                });
            }
        }
    }
})();


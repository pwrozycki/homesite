(function () {
    'use strict';

    angular
        .module('angular')
        .factory('titleService', titleService);

    /* @ngInject */
    function titleService($rootScope, $state, $document, _) {
        var stateToTitleMap = null;

        var service = {
            setTitleForState: setTitleForState
        };

        return service;

        ////////////////

        function setTitleForState(title, stateName) {
            if (stateToTitleMap == null) {
                stateToTitleMap = {};
                setupStateListener();
            }

            if (!stateName) {
                stateName = $state.current.name;
            }

            stateToTitleMap[stateName] = title;
            if ($state.is(stateName)) {
                $document[0].title = title;
            }
        }

        function setupStateListener() {
            $rootScope.$on('$destroy',
                $rootScope.$on('$stateChangeSuccess', setTitleOnRouteChange));
        }

        function setTitleOnRouteChange(event, toState) {
            var currentStateName = toState.name;
            var currentAndParentStates = [currentStateName].concat(getParentStates(currentStateName));

            var mostSpecificStateWithTitle = _.find(currentAndParentStates, function (stateName) {
                if (_.has(stateToTitleMap, stateName)) {
                    return true;
                }
            });

            $document[0].title = stateToTitleMap[mostSpecificStateWithTitle];
        }

        function getParentStates(stateName) {
            var parentStates = [];
            var currentState = stateName;

            while(currentState.indexOf('.') != -1) {
                var parentState = currentState.replace(/^(.*)\..*$/, '$1');
                parentStates.push(parentState);
                currentState = parentState;
            }

            return parentStates;
        }
    }

})();


(function () {
    'use strict';

    var externalDeps = ['ngAnimate', 'ngCookies', 'ngTouch', 'ngSanitize', 'ngMessages', 'ngAria', 'restangular', 'restmod', 'ui.router', 'ui.bootstrap'];
    var myDeps = [];
    angular.module('angular', externalDeps.concat(myDeps));

})();

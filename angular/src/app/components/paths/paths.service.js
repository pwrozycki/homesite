(function () {
    'use strict';

    angular
        .module('angular')
        .factory('pathsService', pathsService);

    /* @ngInject */
    function pathsService() {
        var SEP = '/';

        var service = {
            parentPaths: parentPaths,
            basename: basename,
            dirname: dirname,
            join: join,
            escapeSlashes: escapeSlashes,
            unescapeSlashes: unescapeSlashes
        };

        return service;

        //////////

        function parentPaths(path) {
            if (path === "") {
                return [];
            }

            var pathParents = [];
            var pathSegments = path.split(SEP);
            for (var i = pathSegments.length; i > 0; i--) {
                pathParents.unshift(pathSegments.slice(0, i).join(SEP));
            }
            return pathParents;
        }

        function basename(path) {
            var pathSegments = path.split(SEP);
            return pathSegments[pathSegments.length - 1];
        }

        function dirname(path) {
            var pathSegments = path.split(SEP);
            return pathSegments.slice(0, pathSegments.length - 1).join(SEP);
        }

        function normpath(path) {
            return path.replace(new RegExp(SEP + '+', 'g'), SEP);
        }

        function join() {
            var args = Array.prototype.slice.call(arguments);
            return normpath(args.join(SEP));
        }

        function escapeSlashes(path) {
            return path
                .replace(/'/g, "'_")
                .replace(/\//g, "''");
        }

        function unescapeSlashes(path) {
            return path
                .replace(/''/g, "/")
                .replace(/'_/g, "'");
        }
    }
})();
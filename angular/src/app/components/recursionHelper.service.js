(function () {
    'use strict';

    angular
        .module('angular')
        .factory('recursionHelperService', recursionHelperService);

    /* @ngInject */
    function recursionHelperService($compile) {
        var service = {
            compile: compile
        };
        return service;

        ////////////////

        /**
         * Code understood and copy-pasted from http://stackoverflow.com/a/18609594.
         * @param element
         * @param link
         * @returns {{pre: (link.pre|Function), post: Function}}
         */
        function compile(element, link) {
            // Normalize the link parameter
            if (angular.isFunction(link)) {
                link = {post: link};
            }

            // Break the recursion loop by removing the contents
            var contents = element.contents().remove();
            var compiledContents;

            return {
                pre: (link && link.pre) ? link.pre : null,
                /**
                 * Compiles and re-adds the contents
                 */
                post: function (scope, element) {
                    // Compile the contents
                    if (!compiledContents) {
                        compiledContents = $compile(contents);
                    }

                    // Re-add the compiled contents to the element
                    compiledContents(scope, function (clone) {
                        element.append(clone);
                    });

                    // Call the post-linking function, if any
                    if (link && link.post) {
                        link.post.apply(null, arguments);
                    }
                }
            };
        }
    }

})();


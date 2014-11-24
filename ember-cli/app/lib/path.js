var SEP = '/';

export default {
    /**
     * Return parent paths of given path.
     */
    parentPaths: function(path) {
        var pathParents = [];
        var pathSegments = path.split(SEP);
        for (var i = pathSegments.length; i>0;i--) {
            pathParents.unshift(pathSegments.slice(0, i).join(SEP));
        }
        return pathParents;
    },

    /**
     * Return last component of path.
     */
    basename: function(path) {
        var pathSegments = path.split(SEP);
        return pathSegments[pathSegments.length-1];
    }
};
var SEP = '/';
var TRASH = 'Trash';

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
    },

    /**
     * Return directory. i.e. strip last component.
     */
    dirname: function(path) {
        var pathSegments = path.split(SEP);
        return pathSegments.slice(0, pathSegments.length-1).join(SEP);
    },

    /**
     * Is directory in trash?.
     */
    isInTrash: function (path) {
        return path.indexOf('Trash') === 0;
    },

    /**
     * Directory without 'Trash' prefix.
     */
    outsideTrash: function (path) {
        return this.isInTrash(path) ? path.replace(new RegExp('^' + TRASH + SEP), '') : path;
    },

    /**
     * Directory with 'Trash' prefix.
     */
    insideTrash: function(path) {
        return this.isInTrash(path) ? path : TRASH + SEP + path;
    }
};
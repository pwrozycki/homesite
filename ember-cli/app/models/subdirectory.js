import DS from "ember-data";
import pathlib from '../lib/path';

export default DS.Model.extend({
    path: DS.attr(),
    shared: DS.attr('boolean'),
    parent: DS.belongsTo('directory'),

    /**
     * Name of directory (last component of path).
     */
    name: function () {
        return this.get('path').match(/^.*?([^/]*)$/)[1];
    }.property('path'),

    /**
     * Is directory in trash?.
     */
    inTrash: function () {
        return pathlib.isInTrash(this.get('path'));
    }.property('path'),

    /**
     * Path with / substituted with |.
     */
    pathWithoutSlashes: function () {
        return this.get('path').replace(/\//g, '|');
    }.property('path'),

    /**
     * Parent paths of directory.
     */
    parentDirectories: function () {
        var rootElement = [{path: '.', name: 'ROOT'}];

        // if root - return only root element
        if (this.get('name') === '') {
            return rootElement;
        }

        // otherwise return root elements + elements for parent paths
        return rootElement.concat(pathlib.parentPaths(this.get('path')).map(
            function (el) {
                return { path: el, name: pathlib.basename(el) };
            }
        ));
    }.property('path', 'parent')
});
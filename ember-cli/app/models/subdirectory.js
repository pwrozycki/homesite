import DS from "ember-data";

export default DS.Model.extend({
    path: DS.attr(),
    shared: DS.attr('boolean'),
    thumbnail_path: DS.attr(),
    original_path: DS.attr(),
    preview_path: DS.attr(),

    parent: DS.belongsTo('directory'),

    /**
     * Name of directory (last component of path).
     */
    name: function () {
        return this.get('path') == null ? null : this.get('path').match(/^.*?([^/]*)$/)[1];
    }.property('path'),

    /**
     * Is directory in trash?.
     */
    inTrash: function() {
        return this.get('path').indexOf('Trash') === 0;
    }.property('path'),

    /**
     * Path with / substituted with |.
     */
    pathWithoutSlashes: function() {
        return this.get('path') == null ? null : this.get('path').replace('/', '|')
    }.property('path'),

    /**
     * Parent subpaths of directory.
     */
    parentDirectories: function () {
        var path = this.get('path');
        var directories = [];
        if (path.length > 0) {
            var elements = path.split('/');
            for (var i = 0; i < elements.length; i++) {
                var elementPath = elements.slice(0, elements.length - i).join('|');
                var elementName = elements[elements.length - i - 1];
                directories.push({ path: elementPath, name: elementName});
            }
        }
        directories.push({path: '.', name: 'ROOT'});

        return directories.reverse();
    }.property('path')
});
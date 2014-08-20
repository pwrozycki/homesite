import DS from "ember-data";

export default DS.Model.extend({
    path: DS.attr('string'),
    thumbnail_path: DS.attr('string'),
    preview_path: DS.attr('string'),

    parent: DS.belongsTo('directory'),

    name: function () {
        return this.get('path').match(/^.*?([^/]*)$/)[1];
    }.property('path'),

    inTrash: function() {
        return this.get('path').indexOf('Trash') === 0;
    }.property('path'),

    parentDirectories: function () {
        var path = this.get('path');
        var directories = [];
        if (path.length > 0) {
            var elements = path.split('/');
            for (var i = 0; i < elements.length; i++) {
                var elementPath = elements.slice(0, elements.length - i).join('/');
                var elementName = elements[elements.length - i - 1];
                directories.push({ path: elementPath, name: elementName});
            }
        }
        directories.push({path: '', name: 'ROOT'});

        return directories.reverse();
    }.property('path')
});
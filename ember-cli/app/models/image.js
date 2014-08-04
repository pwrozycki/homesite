import DS from "ember-data";

export default DS.Model.extend({
    name: DS.attr('string'),
    orientation: DS.attr('string'),

    directory: DS.belongsTo('directory'),

    thumbnail: function() {
        return [this.get('directory.thumbnail_path'), this.get('name')].join('/');
    }.property('directory.thumbnail_path', 'name'),

    preview: function() {
        return [this.get('directory.preview_path'), this.get('name')].join('/');
    }.property('directory.preview_path', 'name'),

    path: function() {
        var directoryPath = this.get('directory.path');
        var name = this.get('name');
        return directoryPath === '' ? name : [directoryPath, name].join('/');
    }.property('directory.path', 'name'),

    index: function () {
        var images = this.get('directory.images');

        return images.indexOf(this);
    }.property('directory.images')
});
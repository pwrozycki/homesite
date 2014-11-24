import DS from "ember-data";

var ROTATIONS = ['up', 'right', 'down', 'left'];

export default DS.Model.extend({
    name: DS.attr(),
    orientation: DS.attr(),

    directory: DS.belongsTo('directory'),

    thumbnail: function() {
        return [this.get('directory.thumbnail_path'), this.get('name')].join('/');
    }.property('directory.thumbnail_path', 'name'),

    preview: function() {
        return [this.get('directory.preview_path'), this.get('name')].join('/');
    }.property('directory.preview_path', 'name'),

    original: function() {
        return [this.get('directory.original_path'), this.get('name')].join('/');
    }.property('directory.original_path', 'name'),

    path: function() {
        var directoryPath = this.get('directory.path');
        var name = this.get('name');
        return directoryPath === '' ? name : [directoryPath, name].join('/');
    }.property('directory.path', 'name'),

    index: function () {
        var images = this.get('directory.images');

        return images.indexOf(this);
    }.property('directory.images.@each'),

    isLast: function() {
        return this.get('index') === this.get('directory.images.length') - 1;
    }.property('index', 'directory.images.length'),

    isFirst: function() {
        return this.get('index') === 0;
    }.property('index', 'directory.images.length'),

    nextRotation: function(offset) {
        var currentOrientationIndex = ROTATIONS.indexOf(this.get('orientation'));
        var nextOrientationIndex = (currentOrientationIndex + offset) % ROTATIONS.length;
        return ROTATIONS[nextOrientationIndex];
    }
});
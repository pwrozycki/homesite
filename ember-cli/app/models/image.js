import DS from "ember-data";
import pathlib from "../lib/path";

var ROTATIONS = ['up', 'right', 'down', 'left'];

export default DS.Model.extend({
    orientation: DS.attr(),
    path: DS.attr(),
    directory: DS.belongsTo('directory'),

    /**
     * signifies if some modification to image state is beeing synced to backend.
     * if so no image modification buttons should be active.
     */
    modificationPending: false,

    /**
     * is image selected in browser?
     */
    selected: false,

    name: function() {
        return pathlib.basename(this.get('path'));
    }.property('path'),

    thumbnail: function () {
        return [this.get('collectionInfo.thumbnailsRoot'), this.get('path')].join('/');
    }.property('collectionInfo.thumbnailsRoot', 'path'),

    preview: function () {
        return [this.get('collectionInfo.previewsRoot'), this.get('path')].join('/');
    }.property('collectionInfo.previewsRoot', 'path'),

    original: function () {
        return [this.get('collectionInfo.originalsRoot'), this.get('path')].join('/');
    }.property('collectionInfo.originalsRoot', 'path'),

    index: function () {
        var images = this.get('directory.images');

        return images.indexOf(this);
    }.property('directory.images.@each'),

    next: function () {
        if (this.get('isLast')) {
            return null;
        } else {
            return this.get('directory.images').objectAt(this.get('index') + 1);
        }
    }.property('isLast'),

    previous: function () {
        if (this.get('isFirst')) {
            return null;
        } else {
            return this.get('directory.images').objectAt(this.get('index') - 1);
        }
    }.property('isFirst'),

    isLast: function () {
        return this.get('index') === this.get('directory.images.length') - 1;
    }.property('index', 'directory.images.length'),

    isFirst: function () {
        return this.get('index') === 0;
    }.property('index', 'directory.images.length'),

    nextRotation: function (offset) {
        var currentOrientationIndex = ROTATIONS.indexOf(this.get('orientation'));
        var nextOrientationIndex = (currentOrientationIndex + offset) % ROTATIONS.length;
        return ROTATIONS[nextOrientationIndex];
    }
});
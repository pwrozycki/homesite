import DS from "ember-data";
import File from "./file";

var ROTATIONS = ['up', 'right', 'down', 'left'];

export default File.extend({
    orientation: DS.attr(),
    aspectRatio: DS.attr(),
    thumbnailHeight: 200,

    fileType: 'image',
    isImage: true,

    /**
     * is image selected in browser?
     */
    selected: false,

    thumbnail: function () {
        return [this.get('collectionInfo.thumbnailsRoot'), this.get('path')].join('/');
    }.property('collectionInfo.thumbnailsRoot', 'path'),

    thumbnailWidth: function () {
        return this.get('aspectRatio') * this.get('thumbnailHeight');
    }.property('aspectRatio', 'thumbnailHeight'),

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
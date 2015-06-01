import Subdirectory from "./subdirectory";
import DS from "ember-data";

export default Subdirectory.extend({
    files: DS.hasMany('file', {polymorphic: true, inverse: 'directory'}),
    subdirectories: DS.hasMany('subdirectory', {inverse: 'parent'}),

    /**
     * signifies if cached object can be used or should be reloaded when entering gallery.directory route.
     */
    needsToBeReloaded: false,

    images: function () {
        return this.get('files').filterBy('fileType', 'image');
    }.property('files'),

    videos: function () {
        return this.get('files').filterBy('fileType', 'video');
    }.property('files')
});
import DS from "ember-data";
import pathlib from "../lib/path";

export default DS.Model.extend({
    path: DS.attr(),
    timestamp: DS.attr(),
    directory: DS.belongsTo('directory'),

    /**
     * signifies if some modification to image state is beeing synced to backend.
     * if so no file modification buttons should be active.
     */
    modificationPending: false,

    path_with_timestamp: function() {
        return this.get('path') + '_' + this.get('timestamp');
    }.property('timestamp', 'path'),

    name: function() {
        return pathlib.basename(this.get('path'));
    }.property('path')
});
import DS from "ember-data";
import pathlib from "../lib/path";

export default DS.Model.extend({
    path: DS.attr(),
    directory: DS.belongsTo('directory'),

    /**
     * signifies if some modification to image state is beeing synced to backend.
     * if so no file modification buttons should be active.
     */
    modificationPending: false,

    name: function() {
        return pathlib.basename(this.get('path'));
    }.property('path')
});
import DS from "ember-data";
import pathlib from "../lib/path";

export default DS.Model.extend({
    path: DS.attr(),
    directory: DS.belongsTo('directory'),

    name: function() {
        return pathlib.basename(this.get('path'));
    }.property('path')
});
import DS from "ember-data";

export default DS.Model.extend({
    videosRoot: DS.attr(),
    thumbnailsRoot: DS.attr(),
    previewsRoot: DS.attr(),
    originalsRoot: DS.attr()
});
import DS from "ember-data";

export default DS.Model.extend({
    thumbnailsRoot: DS.attr(),
    previewsRoot: DS.attr(),
    originalsRoot: DS.attr()
});
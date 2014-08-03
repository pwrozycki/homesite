import DS from "ember-data";

export default DS.Model.extend({
    path: DS.attr('string'),
    thumbnail_path: DS.attr('string'),
    preview_path: DS.attr('string'),

    parent: DS.belongsTo('directory', { async: true }),

    name: function () {
        return this.get('path').match(/^.*?([^/]*)$/)[1];
    }.property('path')
});
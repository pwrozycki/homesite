import DS from "ember-data";

export default DS.Model.extend({
    path: DS.attr('string'),
    thumbnailPath: DS.attr('string'),
    previewPath: DS.attr('string'),

    images: DS.hasMany('image', { async: true }),
    parent: DS.belongsTo('directory', { async: true }),
    directories: DS.hasMany('directory', { async: true})
});
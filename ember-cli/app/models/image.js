import DS from "ember-data";

export default DS.Model.extend({
    name: DS.attr('string'),
    orientation: DS.attr('string'),

    directory: DS.belongsTo('image', { async: true })
});
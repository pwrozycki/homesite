import DS from "ember-data";

export default DS.Model.extend({
    redundant: DS.hasMany('image'),
    image: DS.belongsTo('image')
});
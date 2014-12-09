import DS from "ember-data";

export default DS.Model.extend({
    images: DS.hasMany('image'),

    hasAtLeastTwoImages: function() {
        return this.get('images.length') >= 2;
    }.property('images.length')
});
export default Ember.Route.extend({
    serialize: function(model) {
        return { image: model.description };
    },

    model: function(description) {
        return {};
    }
});
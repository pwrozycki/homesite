export default Ember.Route.extend({
    model: function (params, transition) {
        if (!params.directory) {
            this.transitionTo('gallery.browse', '.');
        } else {
            return $.getJSON('http://localhost:18000/gallery/listdir/' + params.directory + '?callback=?');
        }
    }
});

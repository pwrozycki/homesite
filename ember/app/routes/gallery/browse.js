export default Ember.Route.extend({
    model: function (params) {
        if (!params.directory) {
            this.transitionTo('gallery.browse', '.');
            return;
        }

        return  $.getJSON('http://localhost:28000/gallery/listdir/' + params.directory + '?callback=?');
    }
});
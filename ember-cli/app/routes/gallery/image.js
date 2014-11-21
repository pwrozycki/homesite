import Ember from 'ember';

export default Ember.Route.extend({
    model: function(params) {
        // fetch image from gallery.directory controller
        // choose the one with correct name
        var images = this.modelFor('gallery/directory').get('images');
        return images.then(function(images) {
            return images.findBy('name', params.image);
        });
    }
});
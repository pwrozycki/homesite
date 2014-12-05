import Ember from 'ember';

export default Ember.Route.extend({
    model: function (params) {
        // fetch image from gallery.directory controller
        // choose the one with correct name
        var images = this.modelFor('gallery/directory').get('images');
        var image = images.findBy('name', params.image);
        if (Ember.isEmpty(image)) {
            this.transitionTo('gallery.directory');
            return null;
        }
        return  image;
    }
});
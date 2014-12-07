import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        var directory = this.modelFor('gallery.directory');
        return this.store.find('image-group', { directoryId: directory.get('id')});
    }
});
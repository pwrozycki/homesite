import Ember from 'ember';

export default Ember.Route.extend({
    model: function (params) {
        if (!params.directory) {
            this.transitionTo('gallery.browse', '.');
            return;
        }

        return Ember.$.getJSON('/gallery/listdir/' + params.directory + '?callback=?',
            function (json) {
                json.images = Ember.A(json.images);
            }
        );
    }
});
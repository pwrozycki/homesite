import Ember from 'ember';

export default Ember.Route.extend({
    model: function (params) {
        if (!params.directory) {
            this.transitionTo('gallery.browse', '.');
            return;
        }

        return  Ember.$.getJSON('http://raspi:8000/gallery/listdir/' + params.directory + '?callback=?');
    }
});
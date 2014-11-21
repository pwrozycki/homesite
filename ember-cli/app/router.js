import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
    this.resource('gallery', function() {
        this.route('index', {path: '/directory'});
        this.resource('gallery.directory', {path: '/directory/:directory'}, function() {
            this.resource('gallery.image', {path: '/image/:image'});
        })
    });
});

export default Router;

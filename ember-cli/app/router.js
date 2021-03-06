import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

export default Router.map(function() {
  this.resource('gallery', function() {
    this.route('index', {path: '/directory'});
    this.resource('gallery.directory', {path: '/directory/:directory'}, function() {
      this.resource('gallery.directory.image', {path: '/image/:image'});
      this.route('redundant');
    });
  });
});

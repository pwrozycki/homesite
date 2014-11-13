import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
    this.resource('gallery', function() {
        this.route('index', {path: '/browse'});
        this.route('browse', {path: '/browse/*directory'});
    });
});

export default Router;

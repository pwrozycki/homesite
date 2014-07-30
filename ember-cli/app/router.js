import Ember from 'ember';

var Router = Ember.Router.extend({
    location: TestAppENV.locationType
});

Router.map(function () {
    this.resource('gallery', function() {
        this.route('index', {path: '/browse'});
        this.route('browse', {path: '/browse/*directory'});
    });
    this.route('api');
});

export default Router;

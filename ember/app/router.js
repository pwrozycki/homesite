var Router = Ember.Router.extend(); // ensure we don't share routes between all Router instances

Router.map(function () {
    this.resource('gallery', function () {
        this.route('browse', { path: '/browse/*directory'});
    });
});

export default Router;

var Router = Ember.Router.extend(); // ensure we don't share routes between all Router instances

Router.map(function () {
    this.resource('gallery', function () {
        this.resource('gallery.browse', { path: '/browse/:directory'}, function() {
            this.route('preview', { path: '/:image'});
        });
    });
});

export default Router;

var Router = Ember.Router.extend(); // ensure we don't share routes between all Router instances

Router.map(function () {
    this.resource('gallery.browse', { path: '/gallery/browse/*directory' });
});

export default Router;

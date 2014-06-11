function replaceSlashes(index, element) {
    element.path = element.path.replace(/\//g, '|');
}

export default Ember.Route.extend({
    model: function (params, transition) {
        if (!params.directory) {
            this.transitionTo('gallery.browse', '.');
            return;
        }

        var directory = params.directory.replace(/\|/g, '/');
        return $.getJSON('http://localhost:28000/gallery/listdir/' + directory + '?callback=?', function (json) {
            $.each(json.directories, replaceSlashes);
            $.each(json.subdirs, replaceSlashes);
        });
    }
});

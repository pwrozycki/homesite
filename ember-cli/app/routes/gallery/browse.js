import Ember from 'ember';

export default Ember.Route.extend({
    image: null,

    model: function (params) {
        var promise = null;

        if (!params.directory) {
            // if no directory is specified -> lookup root directory
            promise = this.store.find('directory', { root: true });
        } else {
            // if image is specified save it to 'image' instance variable
            // (used later to set previewImage on controller in setupController hook)
            var match = params.directory.match(/^(.*?)(?:\/([^/]*\.jpg))?$/i);
            var image = match[2];
            var directory = match[1];
            if (match.length > 2) {
                this.set('image', image);
            } else {
                this.set('image', null);
            }

            // fetch directory data
            promise = this.store.find('directory', { path: directory});
        }

        return promise.then(
            function (result) {
                return result.objectAt(0);
            }
        );
    },

    setupController: function (controller, model) {
        // set model
        controller.set('model', model);

        // if image is set on route instance, set selected image as previewImage on controller
        if (this.get('image') != null) {
            var self = this;
            model.get('images').then(function(images) {
                var previewImage = images.findBy('name', self.get('image'));
                controller.set('previewImage', previewImage);
            });
        }
    }
});
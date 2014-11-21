import Ember from 'ember';

var $ = Ember.$;

export default Ember.Route.extend({
    images: Ember.computed.alias('controller.model.images'),

    /**
     * Scroll window to top after entering new directory.
     */
    afterModel: function () {
        $(window).scrollTop(0);
    },

    model: function (params) {
        var promise = null;

        if (params.directory === '.') {
            // if no directory is specified -> lookup root directory
            promise = this.store.find('directory', { root: true });
        } else {
            // lookup directory by path
            var directory = params.directory.replace('|', '/');
            promise = this.store.find('directory', { path: directory});
        }

        return promise.then(
            function (result) {
                return result.objectAt(0);
            }
        );
    },

    /**
     * Handle image removal (moving image to trash, or reverting from trash).
     */
    removeImageAjax: function (action, image) {
        var self = this;
        $.post(action + image.get('path')).then(
            // on success: if in preview mode: switch image to next if possible, switch back otherwise
            // leave preview mode if no images left
            function () {
                if (self.controller.get('isPreviewMode')) {
                    if (self.get('images.length') > 1) {
                        self.controllerFor('gallery.image').changeImageAfterRemoval(image);
                    } else {
                        self.transitionTo('gallery.directory');
                    }
                }

                // remove record from list
                var imageIndex = image.get('index');
                self.get('images').replace(imageIndex, 1);
            },
            // on failure: popup modal window containing output message
            function (result) {
                self.send('openModal', 'modals/error-modal', { title: "Server error", html: result.responseText });
            });
    },

    /**
     * When arrow above image is clicked, set orientation to next in cycle.
     */
    rotateImage: function (image, offset) {
        image.set('orientation', image.nextRotation(offset));
        image.save().catch(function () {
            image.set(image.nextRotation(-offset));
        });
    },

    actions: {
        removeImage: function (image) {
            this.removeImageAjax('/gallery/deleteImage/', image);
        },
        revertImage: function (image) {
            this.removeImageAjax('/gallery/revertImage/', image);
        },
        rotateImage: function (image) {
            this.rotateImage(image, 1);
        }
    }
});
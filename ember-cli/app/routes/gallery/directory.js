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
        // sanitize directory
        var directory = params.directory.replace('|', '/');
        if (params.directory === '.') {
            directory = '';
        }

        // try to find directory in store
        var directoryFromStore = this.store.all('directory').findBy('path', directory);
        if (!Ember.isEmpty(directoryFromStore)) {
            return directoryFromStore;
        }

        // perform query otherwise
        // construct queryParams: if root: root=true, path=directory otherwise
        var query = null;
        if (params.directory === '.') {
            query = { root: true };
        } else {
            query = { path: directory };
        }

        return this.store.find('directory', query).then(
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
                image.reload();
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
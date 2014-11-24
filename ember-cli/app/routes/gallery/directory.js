import Ember from 'ember';
import pathlib from '../../lib/path';

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
        var directory = params.directory.replace(/\|/g, '/');
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
     * Reload if needed.
     */
    reloadIfNeeded: function (innerPathObj, outerPathObj, outerPath) {
        if (!Ember.isEmpty(innerPathObj) && Ember.isEmpty(outerPathObj)) {
            var subdirs = innerPathObj.get('subdirectories');
            if (Ember.isEmpty(subdirs.findBy('path', outerPath))) {
                innerPathObj.reload();
            }
        }
    },

    /**
     * Reload directories in trash when image is deleted (i.e moved to trash).
     * Trash directory should be reloaded in following scenario:
     *
     * image 'a/b/img.jpg' is deleted (moved to 'Trash/a/b/img.jpg')
     * prior to deletion:
     * - 'Trash/a' exists and is loaded in store
     * - 'Trash/a/b' dosn't exist
     * after deletion:
     * - 'Trash/a' should be updated to contain 'Trash/b' as one of it's subdirectories
     */
    updateDirectoriesInTrash: function (image) {
        var directory = image.get('directory');
        if (!directory.get('inTrash')) {
            var insideTrashPath = directory.get('insideTrashPath');
            var parentPaths = pathlib.parentPaths(insideTrashPath);
            for (var i = 0; i < parentPaths.length - 1; i++) {
                var outerPath = parentPaths[i + 1];
                var outerPathObj = this.store.all('directory').findBy('path', outerPath);
                var innerPath = parentPaths[i];
                var innerPathObj = this.store.all('directory').findBy('path', innerPath);
                this.reloadIfNeeded(innerPathObj, outerPathObj, outerPath);
            }
        }
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
                self.updateDirectoriesInTrash(image);
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
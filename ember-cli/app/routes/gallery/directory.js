import Ember from 'ember';
import pathlib from '../../lib/path';
import storelib from '../../lib/store';
import lazyloader from '../../utils/lazy-loader';

var $ = Ember.$;

export default Ember.Route.extend({
    images: Ember.computed.alias('controller.model.images'),

    /**
     * Scroll window to top after entering new directory.
     * Launch lazy loader with new images.
     */
    afterModel: function () {
        $(window).scrollTop(0);
        Ember.run.scheduleOnce('afterRender', function () {
            lazyloader.setImages($('img.lazy'));
        });
    },

    /**
     * Return root directory for authenticated - i.e. real root.
     */
    rootDirectoryForAuthenticated: function () {
        return storelib.getUniqueFromCacheOrFetch(this.store, 'directory', {'path': '' }, {root: true });
    },

    /**
     * Return root directory for non authenticated - composed of shared directories (shared=true)
     * displayed as subdirectories of virtual root.
     */
    rootDirectoryForNonAuthenticated: function () {
        var self = this;
        return this.store.find('subdirectory', { shared: 'True' }).then(
            function (subdirs) {
                var rootObject = self.store.createRecord('directory', {path: ''});
                rootObject.get('subdirectories').pushObjects(subdirs);
                return rootObject;
            });
    },

    model: function (params) {
        var sessionController = this.controllerFor('session');
        var self = this;

        // sanitize directory (replace | with /, substitute '.' with '' - ROOT)
        var directory = params.directory.replace(/\|/g, '/');
        if (params.directory === '.') {
            directory = '';
        }

        // Get root directory
        if (directory === '') {
            if (sessionController.get('isAuthenticated')) {
                return this.rootDirectoryForAuthenticated();
            } else {
                return this.rootDirectoryForNonAuthenticated();
            }
            // Get non-root directory as specified by path
        } else {
            return storelib.getUniqueFromCacheOrFetch(this.store, 'directory', { path: directory }).then(
                function (directory) {
                    if (Ember.isEmpty(directory)) {
                        self.transitionTo('gallery.index');
                    }
                    return directory;
                },
                function () {
                    self.transitionTo('gallery.index');
                    return null;
                }
            );
        }
    },

    /**
     * Reload if needed.
     */
    reloadIfNeeded: function (innerPathObj, outerPathObj, outerPath) {
        if (!Ember.isEmpty(innerPathObj) && Ember.isEmpty(outerPathObj)) {
            var subdirs = innerPathObj.get('subdirectories');
            if (Ember.isEmpty(subdirs.findBy('path', outerPath))) {
                return innerPathObj.reload();
            }
        }
        return null;
    },

    /**
     * Reload directories in trash when image is deleted (i.e moved to trash).
     * Trash directory should be reloaded in following scenario:
     *
     * image 'a/b/img.jpg' is deleted (moved to 'Trash/a/b/img.jpg')
     * prior to deletion:
     * - 'Trash/a' exists and is loaded in store
     * - 'Trash/a/b' doesn't exist
     * after deletion:
     * - 'Trash/a' should be updated to contain 'Trash/a/b' as one of it's subdirectories
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
                var promise = this.reloadIfNeeded(innerPathObj, outerPathObj, outerPath);
                if (promise) {
                    return promise;
                }
            }
        }

        return Ember.RSVP.resolve();
    },


    /**
     * Handle image removal (moving image to trash, or reverting from trash).
     */
    removeImageAjax: function (action, image) {
        var self = this;

        var postRemove = $.post(action + image.get('path'));
        image.set('modificationPending', true);
        var nextImage = image.get('next') || image.get('previous');

        Ember.RSVP.resolve(postRemove).then(
            // update data structures from database
            function () {
                image.reload();
                return Ember.RSVP.all([
                        self.updateDirectoriesInTrash(image) ]
                );
            },
            // on failure: popup modal window containing output message
            function (result) {
                self.send('openModal', 'modals/error-modal', { title: "Server error", html: result.responseText });
            }
        ).then(
            // switch image to next if possible, switch back otherwise
            // leave preview mode if no images left
            // update lazyloader in case new images appeared in viewport
            function () {
                if (self.controller.get('isPreviewMode')) {
                    if (nextImage) {
                        self.transitionTo('gallery.image', nextImage.get('name'));
                    } else {
                        self.transitionTo('gallery.directory');
                    }

                } else {
                    lazyloader.update();
                }
            }
        ).finally(
            // disable modification Pending flag (controls whether modification buttons are inactive)
            function () {
                image.set('modificationPending', false);
            }
        );
    },

    /**
     * When arrow above image is clicked, set orientation to next in cycle.
     */
    rotateImage: function (image, offset) {
        image.set('orientation', image.nextRotation(offset));
        image.set('modificationPending', true);

        image.save().catch(function () {
            // if error occurred - revert to previous rotation
            image.set(image.nextRotation(-offset));
        }).finally(function () {
            image.set('modificationPending', false);
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
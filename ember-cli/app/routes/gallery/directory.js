import Ember from 'ember';
import pathlib from '../../lib/path';
import Directory from '../../models/directory';
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
     * Mark directories at opposite side as outdated when image is deleted / reverted from Trash.
     * Trash directory should be reloaded in following scenario:
     *
     * image 'a/b/img.jpg' is deleted (moved to 'Trash/a/b/img.jpg')
     * a.1)
     * prior to deletion:
     * - 'Trash/a' exists and is loaded in store
     * - 'Trash/a/b' doesn't exist
     * after deletion:
     * - 'Trash/a' should be updated to contain 'Trash/a/b' as one of it's subdirectories
     *
     * a.2)
     * prior to deletion:
     * - 'Trash/a/b' exists and is loaded in store
     * after deletion:
     * - 'Trash/a/b' should be updated to contain deleted images
     *
     * b)
     * image 'Trash/a/b/img.jpg' is reverted
     * prior to deletion:
     * - 'a/b' exists and is loaded in store
     * after detetion:
     * - 'a/b' should be updated to contain reverted images
     */
    markDirectoriesAsOutdated: function (directoryPath) {
        var isInTrash = pathlib.isInTrash(directoryPath);
        var oppositeSidePath = isInTrash ? pathlib.outsideTrash(directoryPath) : pathlib.insideTrash(directoryPath);
        var parentPaths = pathlib.parentPaths(oppositeSidePath);

        // image is reverted - only the target directory needs to be updated - i.e. directory to which image
        //                     will be reverted
        // image is deleted - deepest directory in store should be updated -either directory which contains newly
        //                    created directory or directory to which image will be reverted)
        if (isInTrash) {
            parentPaths = parentPaths.slice(parentPaths.length - 1);
        }

        // iterate over parent paths in reverse order
        parentPaths = parentPaths.reverse();
        for (var i = 0; i < parentPaths.length; i++) {

            var path = parentPaths[i];
            var directoryObj = this.store.all('directory').findBy('path', path);

            // mark deepest directory available in store as outdated and exit loop
            if (!Ember.isEmpty(directoryObj)) {
                directoryObj.set('needsToBeReloaded', true);
                break;
            }
        }
    },


    /**
     * Handle image removal (moving image to trash, or reverting from trash).
     */
    removeImageAjax: function (action, image) {
        var self = this;
        var url = '/gallery/api/images/%@/%@'.fmt(image.get('id'), action);

        image.set('modificationPending', true);
        var imagePath = image.get('path');
        var directoryPath = pathlib.dirname(imagePath);

        Ember.RSVP.resolve($.post(url)).then(
            function () {
                // switch image to next if possible, switch back otherwise
                // leave preview mode if no images left
                // update lazyloader in case new images appeared in viewport
                if (self.controller.get('isPreviewMode')) {
                    var nextImage = image.get('next') || image.get('previous');
                    if (nextImage) {
                        self.transitionTo('gallery.directory.image', nextImage.get('name'));
                    } else {
                        self.transitionTo('gallery.directory');
                    }

                }

                lazyloader.update();

                // remove image from directory
                var directory = self.store.all('directory').findBy('path', directoryPath);
                if (! Ember.isEmpty(directory)) {
                    directory.get('images').removeObject(image);
                }

                // remove image from image groups
                self.store.all('image-group').forEach(function(imageGroup) {
                    var images = imageGroup.get('images');
                    images.removeObject(images.findBy('path', imagePath));
                });

                // mark opposite directory as outdated
                self.markDirectoriesAsOutdated(directoryPath);
            },
            // on failure: popup modal window containing output message
            function (result) {
                self.send('openModal', 'modals/error-modal', { title: "Server error", html: result.responseText });
            }
        ).finally(
            // disable modification pending flag (controls whether modification buttons are inactive)
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
            this.removeImageAjax('trash', image);
        },
        revertImage: function (image) {
            this.removeImageAjax('revert', image);
        },
        rotateImage: function (image) {
            this.rotateImage(image, 1);
        }
    }
});
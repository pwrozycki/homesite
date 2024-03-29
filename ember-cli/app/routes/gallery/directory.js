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
        return storelib.getUniqueFromCacheOrFetch(this.store, 'directory', {'path': ''}, {root: true});
    },

    /**
     * Return root directory for non authenticated - composed of shared directories (shared=true)
     * displayed as subdirectories of virtual root.
     */
    rootDirectoryForNonAuthenticated: function () {
        var self = this;
        return this.store.find('subdirectory', {shared: 'True'}).then(
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
            return storelib.getUniqueFromCacheOrFetch(this.store, 'directory', {path: directory}).then(
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
    markDirectoriesAsOutdated: function (dirDstPath) {
        var parentPaths = pathlib.parentPaths(dirDstPath);

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
     * Switch to different image - current has been removed
     */
    changeImageAfterRemoval: function (image) {
        // switch image to next if possible, switch back otherwise
        // leave preview mode if no images left
        if (this.controller.get('isPreviewMode')) {
            var nextImage = image.get('next') || image.get('previous');
            if (nextImage) {
                this.transitionTo('gallery.directory.image', nextImage.get('name'));
            } else {
                this.transitionTo('gallery.directory');
            }

        }
    },

    /**
     * Move image.
     */
    moveImage: function (media_file, dirDstPath, batchMode) {
        var self = this;

        media_file.set('modificationPending', true);
        var imageSrcPath = media_file.get('path');

        var dirSrcPath = pathlib.dirname(imageSrcPath);

        var url = '/gallery/api/files/%@/move'.fmt(media_file.get('id'));
        var data = {move: {destination: dirDstPath}};

        var promise = $.ajax(url, {
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST'
        });

        return Ember.RSVP.resolve(promise).then(
            function () {
                var fileIsImage = media_file.get('fileType') === 'image';
                if (fileIsImage) {
                    self.changeImageAfterRemoval(media_file);
                }

                // update lazyloader in case new images appeared in viewport
                // it will be done later when in batch mode
                if (batchMode !== true) {
                    lazyloader.update();
                }

                // remove image from directory
                var directory = self.store.all('directory').findBy('path', dirSrcPath);
                if (!Ember.isEmpty(directory)) {
                    directory.get('files').removeObject(media_file);
                }

                if (fileIsImage) {
                    // remove image from image groups
                    self.store.all('image-group').forEach(function (imageGroup) {
                        var images = imageGroup.get('images');
                        images.removeObject(images.findBy('path', imageSrcPath));
                    });
                }

                // mark opposite directory as outdated
                self.markDirectoriesAsOutdated(dirDstPath);
            },
            // on failure: popup modal window containing output message
            function (result) {
                self.send('openModal', 'modals/error-modal', {title: "Server error", html: result.responseText});
            }
        ).finally(
            // disable modification pending flag (controls whether modification buttons are inactive)
            function () {
                media_file.set('modificationPending', false);
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

    /**
     * Sequentially move images, to dstPath.
     */
    moveImages: function (images, dstPath) {
        if (images.length <= 0) {
            return;
        }

        var image = images.pop();
        var self = this;

        // proceed with moving next image when first is moved
        this.moveImage(image, dstPath).then(function () {
            self.moveImages(images, dstPath);
        });
    },

    actions: {
        moveSelection: function (selectedImages, dstDir) {
            this.moveImages(selectedImages, dstDir);
        },

        removeFile: function (image) {
            var pathInsideTrash = pathlib.dirname(pathlib.insideTrash(image.get('path')));
            this.moveImage(image, pathInsideTrash);
        },

        revertFile: function (image) {
            var pathOutsideTrash = pathlib.dirname(pathlib.outsideTrash(image.get('path')));
            this.moveImage(image, pathOutsideTrash);
        },

        rotateImage: function (image) {
            this.rotateImage(image, 1);
        }
    }
});
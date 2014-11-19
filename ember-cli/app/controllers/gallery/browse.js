import Ember from 'ember';

var $ = Ember.$;

export default Ember.ObjectController.extend({
    needs: ['session'],
    session: Ember.computed.alias('controllers.session'),

    previewImage: null,

    isPreviewMode: function () {
        return this.get('previewImage') != null;
    }.property('previewImage'),

    isBrowserVisible: function () {
        return !this.get('isPreviewMode');
    }.property('isPreviewMode'),

    scrollTopOnDirectoryChange: function () {
        $(window).scrollTop(0);
    }.observes('path'),

    changeUrlOnPreviewChange: function () {
        // TODO: it would be better to somehow deduce from route name and model (directory object)
        var hashMatch = location.hash.match(/^(#.*?)(?:\/([^/]*\.jpg))?$/i);
        var directory = hashMatch[1];

        // if previewImage is set, add image name to url hash
        // if previewImage is unset, strip image name from url hash
        var newHashUrl = null;
        if (this.get('previewImage') != null) {
            newHashUrl = [directory, this.get('previewImage.name')].join('/');
        } else {
            newHashUrl = directory;
        }

        history.pushState(null, null, newHashUrl);
    }.observes('previewImage'),

    setupImagePreloading: function (newImageIndex, sign) {
        var images = this.get('images');

        // Calculate paths of images that should be preloaded
        var newPreviewPaths = new Ember.Set();
        for (var i = 0; Math.abs(i) < 10; i += sign) {
            var preloadIndex = newImageIndex + i;
            if (preloadIndex >= 0 && preloadIndex < images.get('length')) {
                newPreviewPaths.add(images.objectAt(preloadIndex).get('preview'));
            }
        }

        $("#preloads").find("img").each(function (index, item) {
            var previewPath = $(item).attr('src');

            // Remove img objects that should no longer be in preloaded
            // Remove paths from set, if corresponding img object already exists
            if (!newPreviewPaths.contains(previewPath)) {
                $(this).remove();
            } else {
                newPreviewPaths.remove(previewPath);
            }
        });

        var $previewImg = $("#preview-image").find("> img");
        $previewImg.unbind('load');
        $previewImg.bind('load', function () {
            // Add img object if there is no corresponding preload for path
            newPreviewPaths.forEach(function (item) {
                $("#preloads").append($("<img>", { src: item }));
            });
        });
    },

    switchToImage: function (sign) {
        var images = this.get('images');
        var newImageIndex = this.get('previewImage.index') + sign;
        if (newImageIndex < images.get('length') && newImageIndex >= 0) {
            this.set('previewImage', images.objectAt(newImageIndex));
        }

        this.setupImagePreloading(newImageIndex, sign);
    },

    scrollToImage: function (index) {
        var images = this.get('images');
        var imagesLength = images.get('length');
        if (imagesLength <= 0) {
            return;
        }

        var imageIndex = index;
        if (index >= imagesLength) {
            imageIndex = imagesLength - 1;
        }
        if (index < 0) {
            imageIndex = 0;
        }

        var $image = $('img[data-name="' + images.objectAt(imageIndex).get('name') + '"]');
        if ($image.length) {
            $(window).scrollTop($image.offset().top + $image.height() / 2 - $(window).height() / 2);
        }
    },

    returnToBrowser: function (returnImageIndex) {
        var previewImageIndex;
        if (typeof returnImageIndex === 'undefined') {
            previewImageIndex = this.get('previewImage.index');
        } else {
            previewImageIndex = returnImageIndex;
        }

        this.set('previewImage', null);

        var self = this;
        Ember.run.scheduleOnce('afterRender', function () {
            self.scrollToImage(previewImageIndex);
        });
    },

    removeImageAjax: function (action, image) {
        var self = this;
        $.post(action + image.get('path')).then(
            function () {
                var imagesCount = self.get('images.length');
                var imageIndex = image.get('index');

                // from preview mode siwtch to next image (unless last)
                // to previous (otherwise) or return to browsing (if no images left)
                if (self.get('previewImage') != null) {
                    if (imageIndex + 1 < imagesCount) {
                        self.switchToImage(1);
                    } else if (imageIndex > 0) {
                        self.switchToImage(-1);
                    } else {
                        self.returnToBrowser(imageIndex);
                    }
                }

                // remove record from store
                self.get('images').replace(imageIndex, 1);
            },
            function (result) {
                self.send('openModal', 'modals/error-modal', { title: "Server error", html: result.responseText });
            });
    },

    rotateImage: function (image, offset) {
        image.set('orientation', image.nextRotation(offset));
        image.save().catch(function () {
            image.set(image.nextRotation(-offset));
        });
    },

    actions: {
        login: function() {
            this.get('controllers.session').login();
        },
        logout: function() {
            this.get('controllers.session').logout();
        },
        toggleShared: function(directory) {
            // directory.parent should be fetched, otherwise required parent field isn't supplied
            // when performing save operation
            directory.get('parent').then(function() {
                var oldShared = directory.get('shared');
                directory.set('shared', !oldShared);
                directory.save().catch(function () {
                    directory.set('shared', oldShared);
                });
            });
        },
        showPreview: function (image) {
            this.set('previewImage', image);
        },
        exitPreview: function () {
            this.returnToBrowser();
        },
        nextImage: function () {
            this.switchToImage(1);
        },
        prevImage: function () {
            this.switchToImage(-1);
        },
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
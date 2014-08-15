import Ember from 'ember';

export default Ember.ObjectController.extend({
    previewImage: null,

    isPreviewMode: function () {
        return this.get('previewImage') != null;
    }.property('previewImage'),

    isBrowserVisible: function () {
        return !this.get('isPreviewMode');
    }.property('isPreviewMode'),

    switchToImage: function (offset) {
        var images = this.get('images');
        var newImageIndex = this.get('previewImage.index') + offset;
        if (newImageIndex < images.get('length') && newImageIndex >= 0) {
            this.set('previewImage', images.objectAt(newImageIndex));
        }
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

        var $image = Ember.$('img[data-name="' + images.objectAt(imageIndex).get('name') + '"]');
        if ($image.length) {
            Ember.$(window).scrollTop($image.offset().top + $image.height() / 2 - Ember.$(window).height() / 2);
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
        Ember.$.post(action + image.get('path'), function () {
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
            image.get('directory.images').removeRecord(image);
        });
    },

    rotateImage: function(image, offset) {
        image.set('orientation', image.nextRotation(offset));
        image.save().catch(function() {
            image.set(image.nextRotation(-offset));
        });
    },

    actions: {
        preview: function (image) {
            this.set('previewImage', image);
        },
        browse: function () {
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
import Ember from 'ember';

export default Ember.ObjectController.extend({
    previewImage: null,

    isPreviewMode: function () {
        return this.get('previewImage') != null;
    }.property('previewImage'),

    isBrowserVisible: function () {
        return !this.get('isPreviewMode');
    }.property('isPreviewMode'),

    imageIndex: function(image) {
        var images = this.get('model.images');
        for (var i = 0; i < images.length; i++) {
            if (images[i].description === image.description) {
                return i;
            }
        }
    },

    currentImageIndex: function () {
        var previewImage = this.get('previewImage');
        return this.imageIndex(previewImage);
    },

    switchToImage: function (offset) {
        var images = this.get('model.images');
        var newImageIndex = this.currentImageIndex() + offset;
        if (newImageIndex < images.length && newImageIndex >= 0) {
            this.set('previewImage', images[newImageIndex]);
        }
    },

    scrollToImage: function (index) {
        var images = this.get('model.images');
        if (images.length <= 0) {
            return;
        }

        var imageIndex = index;
        if (index >= images.length) {
            imageIndex = images.length - 1;
        }
        if (index < 0) {
            imageIndex = 0;
        }

        var image = Ember.$('img[data-name="' + images[imageIndex].description + '"]');
        if (image.length) {
            Ember.$(window).scrollTop(image.offset().top + image.height() / 2 - Ember.$(window).height() / 2);
        }
    },

    returnToBrowser: function(returnImageIndex) {
        var previewImageIndex;
        if (typeof returnImageIndex === 'undefined') {
            previewImageIndex = this.currentImageIndex();
        } else {
            previewImageIndex = returnImageIndex;
        }

        this.set('previewImage', null);

        var self = this;
        Ember.run.scheduleOnce('afterRender', function() {
            self.scrollToImage(previewImageIndex);
        });
    },

    removeImage: function (imageIndex) {
        this.get('model.images').replace(imageIndex, 1);
    },

    postRemoveAction: function (action, image) {
        var self = this;
        Ember.$.post(action + image.path, function () {
            var imageIndex = self.imageIndex(image);
            self.removeImage(imageIndex);
            self.returnToBrowser(imageIndex);
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
            this.postRemoveAction('/gallery/deleteImage/', image);
        },
        revertImage: function (image) {
            this.postRemoveAction('/gallery/revertImage/', image);
        }
    }
});
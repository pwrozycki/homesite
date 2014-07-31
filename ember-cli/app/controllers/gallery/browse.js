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
            var imageIndex = image.get('index');
            image.deleteRecord();
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
            this.removeImageAjax('/gallery/deleteImage/', image);
        },
        revertImage: function (image) {
            this.removeImageAjax('/gallery/revertImage/', image);
        }
    }
});
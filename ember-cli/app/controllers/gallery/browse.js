import Ember from 'ember';

export default Ember.ObjectController.extend({
    previewImage:null,

    isPreviewMode: function() {
        return this.get('previewImage') != null;
    }.property('previewImage'),

    isBrowserVisible: function() {
        return ! this.get('isPreviewMode');
    }.property('isPreviewMode'),

    currentImageIndex: function () {
        var images = this.get('model.images');
        var previewImage = this.get('previewImage');
        for (var i = 0; i < images.length; i++) {
            if (images[i].description === previewImage.description) {
                return i;
            }
        }
    },

    switchToImage: function (offset) {
        var images = this.get('model.images');
        var newImageIndex = this.currentImageIndex() + offset;
        if (newImageIndex < images.length && newImageIndex >= 0) {
            this.set('previewImage', images[newImageIndex]);
        }
    },

    actions: {
        preview: function (image) {
            this.set('previewImage', image);
        },
        browse: function () {
            this.set('previewImage', null);
        },
        nextImage: function () {
            this.switchToImage(1);
        },
        prevImage: function () {
            this.switchToImage(-1);
        }
    }
});
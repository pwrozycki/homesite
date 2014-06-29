import Ember from 'ember';

export default Ember.ObjectController.extend({
    init: function () {
        this.set('isPreviewMode', false);
    },

    _currentImageIndex: function () {
        var images = this.get('model.images');
        var previewImage = this.get('previewImage');
        for (var i = 0; i < images.length; i++) {
            if (images[i].description === previewImage.description) {
                return i;
            }
        }
    },

    _switchToImage: function (offset) {
        var images = this.get('model.images');
        var newImageIndex = this._currentImageIndex() + offset;
        if (newImageIndex < images.length && newImageIndex >= 0) {
            this.set('previewImage', images[newImageIndex]);
        }
    },

    actions: {
        preview: function (image) {
            this.set('previewImage', image);
            this.set('isPreviewMode', true);
        },
        browse: function () {
            this.set('isPreviewMode', false);

        },
        nextImage: function () {
            this._switchToImage(1);
        },
        prevImage: function () {
            this._switchToImage(-1);
        }
    }
});
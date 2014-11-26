import Ember from 'ember';
import preloader from '../../utils/preloader';
import lazyloader from '../../utils/lazy-loader';

export default Ember.ObjectController.extend({
    needs: ['gallery/directory'],
    images: Ember.computed.alias('controllers.gallery/directory.images'),

    /**
     * Handle image removal properly.
     * Switch to next image (unless last), to previous (otherwise).
     */
    changeImageAfterRemoval: function (image) {
        var imageIndex = image.get('index');
        var imagesCount = this.get('images.length');
        var self = this;

        if (imageIndex + 1 < imagesCount) {
            self.switchToImage(1);
        } else if (imageIndex > 0) {
            self.switchToImage(-1);
        }
    },

    /**
     * Switch to image specified by sign argument.
     * 1 - next image, -1 - previous image
     */
    switchToImage: function (sign) {
        var images = this.get('images');
        var newImageIndex = this.get('model.index') + sign;
        if (newImageIndex < images.get('length') && newImageIndex >= 0) {
            var newImage = images.objectAt(newImageIndex);
            this.transitionToRoute('gallery.image', newImage.get('name'));
        }

        preloader.setupImagePreloading(images, newImageIndex, sign);
    },

    actions: {
        exitPreview: function (image) {
            lazyloader.rebindEvents();
            this.transitionToRoute('gallery.directory', {queryParams: {scrollTo: image.get('name')}});
        },
        nextImage: function () {
            this.switchToImage(1);
        },
        prevImage: function () {
            this.switchToImage(-1);
        }
    }
});
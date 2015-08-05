import Ember from 'ember';
import preloader from '../../../utils/preloader';
import lazyloader from '../../../utils/lazy-loader';

export default Ember.Controller.extend({
    needs: ['gallery/directory'],
    images: Ember.computed.alias('controllers.gallery/directory.model.images'),

    /**
     * Switch to image specified by sign argument.
     * 1 - next image, -1 - previous image
     */
    switchToImage: function (newImage) {
        if (newImage) {
            this.transitionToRoute('gallery.directory.image', newImage.get('name'));
            preloader.setupImagePreloading(this.get('images'), newImage.get('index'));
        }
    },

    actions: {
        exitPreview: function (image) {
            lazyloader.rebindEvents();
            this.transitionToRoute('gallery.directory', {queryParams: {scrollTo: image.get('name')}});
        },
        nextImage: function () {
            this.switchToImage(this.get('model.next'));
        },
        prevImage: function () {
            this.switchToImage(this.get('model.previous'));
        }
    }
});
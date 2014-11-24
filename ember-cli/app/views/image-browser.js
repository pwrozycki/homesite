import Ember from 'ember';
import lazyloader from '../tools/lazy-loader';

function updateCallback() {
    lazyloader.update();
}

function setupLazyLoader() {
    lazyloader.setImages(Ember.$("img.lazy"));
}

export default Ember.View.extend({
    templateName: 'views/image-browser',

    /**
      * Defer all lazyloader operations until images are loaded.
      */
    runAfterImagesLoadedInAfterRednerPhase: function(callback) {
        this.get('controller.model.images').then(function () {
            Ember.run.scheduleOnce('afterRender', callback);
        });
    },

    /**
     * Disable or enable lazyloader when visibility changes.
     */
    isVisibleChanged: function() {
        if (this.get('isVisible')) {
            lazyloader.rebindEvents();
        } else {
            lazyloader.unbindEvents();
        }
    }.observes('isVisible'),

    /**
     * When browser is inserted to DOM or when model (directory) is changed lazy loader is reset.
     */
    setupLazyLoader: function () {
        this.runAfterImagesLoadedInAfterRednerPhase(setupLazyLoader);
    }.on('didInsertElement').observes('controller.model'),

    /**
     * When image list is modified call lazy loader update.
     */
    imageUrlsChanged: function () {
        this.runAfterImagesLoadedInAfterRednerPhase(updateCallback);
    }.observes('controller.model.images.@each.name')
});

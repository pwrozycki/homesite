import Ember from 'ember';
import LazyLoader from '../tools/lazy-loader';

var lazyLoader = LazyLoader.create({});

function updateCallback() {
    lazyLoader.update();
}

function setupLazyLoader() {
    lazyLoader.setImages(Ember.$("img.lazy"));
}

export default Ember.View.extend({
    templateName: 'views/image-browser',

    /**
      * Defer all lazyloader operations until images are loaded.
      */
    runAfterImagesLoadedInAfterRednerPhase: function(callback) {
        this.get('controller.model.images').then(function () {
            Ember.run.scheduleOnce('afterRender', callback);
        })
    },

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

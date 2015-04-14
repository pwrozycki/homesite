import Ember from 'ember';

var $ = Ember.$;

import lazyloader from '../../utils/lazy-loader';

export default Ember.Controller.extend({
    needs: ['application'],
    currentRouteName: Ember.computed.alias('controllers.application.currentRouteName'),

    queryParams: ['scrollTo'],
    scrollTo: null,

    /**
     * Reset store after sign-in / sign-out.
     * Go to 'gallery.index' to reload models.
     */
    resetAfterAuthenticate: function () {
        this.store.unloadAll('directory');
        this.store.unloadAll('subdirectory');
        this.store.unloadAll('image');
        this.transitionToRoute('gallery.index');
    }.observes('session.isAuthenticated'),

    /**
     * Determine if gallery is in preview mode.
     */
    isPreviewMode: function () {
        return this.get('currentRouteName') === 'gallery.directory.image';
    }.property('currentRouteName'),

    /**
     * Determine if gallery is in browsing mode.
     */
    isBrowserVisible: function () {
        console.log(this.get('currentRouteName'));
        return this.get('currentRouteName') === 'gallery.directory' ||
            this.get('currentRouteName') === 'gallery.directory.index';
    }.property('currentRouteName'),

    /**
     * Determine if redundant images mode is selected.
     */
    isRedundantImagesMode: function () {
        return this.get('currentRouteName') === 'gallery.directory.redundant';
    }.property('currentRouteName'),

    /**
     * Determine if any of images has been selected.
     */
    isSelectionMode: function () {
        return this.get('model.images').isAny('selected', true);
    }.property('model.images.@each.selected'),

    /**
     * Scroll to image as passed in scrollTo request parameter.
     */
    scrollToImage: function () {
        var imageName = this.get('scrollTo');
        var images = this.get('model.images');

        // scroll is performed when images are resolved in afterRender phase
        // (otherwise jQuery wouldn't find any images in DOM)
        if (images != null && imageName != null) {
            Ember.run.schedule('afterRender', function () {
                var $image = $('img[data-name="' + imageName + '"]');
                if ($image.length) {
                    $(window).scrollTop($image.offset().top + $image.height() / 2 - $(window).height() / 2);
                }
            });
        }
    }.observes('scrollTo', 'model.images'),

    actions: {
        showPreview: function (image) {
            lazyloader.unbindEvents();
            this.transitionToRoute('gallery.directory.image', image.get('name'), {queryParams: {scrollTo: null}});
        }
    }
});
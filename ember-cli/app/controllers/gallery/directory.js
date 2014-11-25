import Ember from 'ember';

var $ = Ember.$;

export default Ember.ObjectController.extend({
    needs: ['application'],
    currentRouteName: Ember.computed.alias('controllers.application.currentRouteName'),

    queryParams: ['scrollTo'],
    scrollTo: null,

    /**
     * Determine if gallery is in preview mode.
     */
    isPreviewMode: function () {
        return this.get('currentRouteName') === 'gallery.image';
    }.property('currentRouteName'),

    /**
     * Determine if gallery is in browsing mode.
     */
    isBrowserVisible: function () {
        return !this.get('isPreviewMode');
    }.property('isPreviewMode'),

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
        toggleShared: function (directory) {
            var oldShared = directory.get('shared');
            directory.set('shared', !oldShared);
            directory.save().catch(function () {
                directory.set('shared', oldShared);
            });
        }
    }
});
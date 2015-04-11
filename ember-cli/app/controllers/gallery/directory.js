import Ember from 'ember';

var $ = Ember.$;

import lazyloader from '../../utils/lazy-loader';

export default Ember.ObjectController.extend({
    needs: ['application'],
    currentRouteName: Ember.computed.alias('controllers.application.currentRouteName'),

    queryParams: ['scrollTo'],
    scrollTo: null,

    // Selection view parameters
    destinationFolder: null,
    selectedFolderFocus: null,
    fetchFoldersRun: null,

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
     * Clear selected images.
     */
    clearSelection: function () {
        this.get('model.images').filterBy('selected', true).forEach(function (image) {
            image.set('selected', false);
        });
    }.observes('model.images'),

    /**
     * Number of selected images.
     */
    numSelectedImages: function () {
        return this.get('model.images').filterBy('selected', true).length;
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

    /**
     * Search for autocomplete results
     */
    fetchMatchingFolders: function () {
        this.set('matchingFolders', null);

        var destinationFolder = this.get('destinationFolder');

        // search for the term specified by user
        if (!Ember.isEmpty(destinationFolder)) {
            var self = this;

            // cancel pending fetching of matching folders
            if (!Ember.isEmpty(this.fetchFoldersRun)) {
                Ember.run.cancel(this.fetchFoldersRun);
            }

            // schedule new search
            this.fetchFoldersRun = Ember.run.later(
                function () {
                    var destinationFolderSearch = destinationFolder.replace(new RegExp('/', 'g'), '|');
                    self.store.find('subdirectory', {path_like: destinationFolderSearch}).then(
                        function (result) {
                            self.set('matchingFolders', result.mapBy('path'));
                        });
                },
                300);
        }
    }.observes('destinationFolder'),

    actions: {
        selectOption: function (option) {
            this.set('destinationFolder', option);
        },

        clearSelection: function () {
            this.clearSelection();
        },

        showPreview: function (image) {
            lazyloader.unbindEvents();
            this.transitionToRoute('gallery.directory.image', image.get('name'), {queryParams: {scrollTo: null}});
        },

        toggleShared: function (directory) {
            var oldShared = directory.get('shared');
            directory.set('shared', !oldShared);
            directory.save().catch(function () {
                directory.set('shared', oldShared);
            });
        }
    }
});
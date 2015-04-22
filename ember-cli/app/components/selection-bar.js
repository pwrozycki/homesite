import Ember from 'ember';

export default Ember.Component.extend({
    classNames: ['selectionbar'],
    classNameBindings: ['visible::hidden'],

    // Selection view parameters
    destinationFolder: null,
    matchingFolders: null,
    selectedFolderFocus: false,
    fetchFoldersRun: null,

    /**
     * Number of selected images.
     */
    numSelectedImages: function () {
        return this.get('model.images').filterBy('selected', true).length;
    }.property('model.images.@each.selected'),


    /**
     * Clear selected images.
     */
    clearSelection: function () {
        this.get('model.images').filterBy('selected', true).forEach(function (image) {
            image.set('selected', false);
        });
    }.observes('model.images'),

    // TODO: consider: move code responsible for fetching data, outside component
    /**
     * Search for autocomplete results
     */
    fetchMatchingFolders: function () {
        this.set('matchingFolders', null);
        var destinationFolder = this.get('destinationFolder');

        // search for the term specified by user
        if (!Ember.isEmpty(destinationFolder)) {
            var self = this;
            var store = this.get('targetObject.store');

            // cancel pending fetching of matching folders
            if (!Ember.isEmpty(this.fetchFoldersRun)) {
                Ember.run.cancel(this.fetchFoldersRun);
            }

            // schedule new search
            this.fetchFoldersRun = Ember.run.later(
                function () {
                    var destinationFolderSearch = destinationFolder.replace(new RegExp('/', 'g'), '|');
                    store.find('subdirectory', {path_like: destinationFolderSearch}).then(
                        function (result) {
                            self.set('matchingFolders', result.mapBy('path'));
                        });
                },
                300);
        }
    }.observes('destinationFolder'),

    autocompleteListShown: function() {
        return !Ember.isEmpty(this.get('matchingFolders')) && this.get('selectedFolderFocus');
    }.property('matchingFolders', 'selectedFolderFocus'),

    actions: {
        selectOption: function (option) {
            this.set('destinationFolder', option);
        },

        clearSelection: function () {
            this.clearSelection();
        },

        moveSelection: function() {
            var selectedImages = this.get('model.images').filterBy('selected', true);
            var dstFolder = this.get('destinationFolder');
            this.sendAction('moveSelection', selectedImages, dstFolder);
        }
    }
});
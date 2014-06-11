export default Ember.View.extend({
    templateName: 'gallery/preview-view',

    didInsertElement: function() {
        $("#dirlisting, #directorybar, #images").hide();
    },

    willDestroyElement: function() {
        this.set('isVisible', false);
        $("#dirlisting, #directorybar, #images").show();
    }
});
export default Ember.Component.extend({
    didInsertElement: function () {
        $("img.lazy").lazyload();
    },

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        }
    }
});

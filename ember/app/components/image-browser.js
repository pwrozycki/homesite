export default Ember.Component.extend({
    didInsertElement: function () {
        $("img.lazy").lazyload({ threshold: 200 });
    },

    imagesChanged: function() {
        this.rerender();
    }.observes('images'),

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        }
    }
});

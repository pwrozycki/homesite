import Ember from 'ember';

export default Ember.Component.extend({
    lazyLoadImages: function () {
        Ember.$(window).unbind("scroll");
        Ember.$(window).unbind("resize");
        Ember.$("img.lazy").lazyload({ threshold: 200 });
    }.on('didInsertElement'),

    imagesChanged: function () {
        var $this = this;
        Ember.run.scheduleOnce('afterRender', function () {
            $this.lazyLoadImages();
        });
    }.observes('model.images.@each.thumbnail'),

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        },
        remove: function (image) {
            this.sendAction('removePressed', image);
        },
        undo: function (image) {
            this.sendAction('undoPressed', image);
        },
        rotate: function (image) {
            this.sendAction('rotatePressed', image);
        }
    }
});

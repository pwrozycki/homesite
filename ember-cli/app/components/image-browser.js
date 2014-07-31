import Ember from 'ember';

export default Ember.Component.extend({
    lazyLoadImages: function () {
        Ember.$("img.lazy").lazyload({ threshold: 200 });
    }.on('didInsertElement'),

    imagesChanged: function () {
        var $this = this;
        this.get('model.images').then(function () {
            Ember.run.scheduleOnce('afterRender', function () {
                $this.lazyLoadImages();
            });
        });
    }.observes('model.images.@each.thubnail'),

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        },
        remove: function (image) {
            this.sendAction('removePressed', image);
        },
        undo: function (image) {
            this.sendAction('undoPressed', image);
        }
    }
});

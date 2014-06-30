import Ember from 'ember';

export default Ember.Component.extend({
    lazyLoadImages: function() {
        Ember.$("img.lazy").lazyload({ threshold: 200 });
    }.on('didInsertElement'),
        
    imagesChanged: function() {
        var $this = this;
        Ember.run.scheduleOnce('afterRender', function() {
            $this.lazyLoadImages();
        });
    }.observes('model.images'),

    actions: {
        imageClicked: function (image) {
            this.sendAction('imageClicked', image);
        }
    }
});

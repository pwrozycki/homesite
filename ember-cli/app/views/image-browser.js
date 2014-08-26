import Ember from 'ember';

export default Ember.View.extend({
    templateName: 'views/image-browser',

    lazyLoadImages: function () {
        Ember.$(window).unbind("scroll");
        Ember.$(window).unbind("resize");
        Ember.$("img.lazy").lazyload({ threshold: 200 });
    }.on('didInsertElement'),

    // Reload lazyload plugin, when images where changed
    imagesChanged: function () {
        var $this = this;
        Ember.run.scheduleOnce('afterRender', function () {
            $this.lazyLoadImages();
        });
    }.observes('controller.model.images.@each')
});

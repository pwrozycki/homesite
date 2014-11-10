import Ember from 'ember';
import LazyLoader from '../tools/lazy-loader';

var lazyLoader = LazyLoader.create({});
var $ = Ember.$;

function updateCallback() {
    lazyLoader.update();
}

export default Ember.View.extend({
    templateName: 'views/image-browser',

    setupLazyLoader: function () {
        lazyLoader.setImages($("img.lazy"));
    }.on('didInsertElement'),

    imageUrlsChanged: function () {
        Ember.run.scheduleOnce('afterRender', updateCallback);
    }.observes('controller.model.images.@each.name'),

    imagesChanged: function () {
        Ember.run.scheduleOnce('afterRender', this.setupLazyLoader.bind(this));
    }.observes('controller.model.directory')
});

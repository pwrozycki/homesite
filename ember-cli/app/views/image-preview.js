import Ember from 'ember';

export default Ember.View.extend({
    templateName: 'views/image-preview',

    setKeyEventHandlers: function () {
        var self = this;
        Ember.$(window).keyup(function (event) {
            // left arrow
            if (event.which === 37) {
                self.get('controller').send('prevImage');

            // right arrow
            } else if (event.which === 39) {
                self.get('controller').send('nextImage');

            // up arrow or escape key
            } else if (event.which === 38 || event.which === 27) {
                self.get('controller').send('exitPreview', self.get('controller.model'));

            // delete key
            } else if (event.which === 46) {
                var previewImage = self.get('controller.model');
                self.get('controller').send('removeImage', previewImage);
            }
        });
    }.on('didInsertElement'),

    removeKeyEventHandlers: function () {
        Ember.$(window).unbind("keyup");
    }.on('willDestroyElement')
});

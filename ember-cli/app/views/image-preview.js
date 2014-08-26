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
                self.get('controller').send('exitPreview');

            // delete key
            } else if (event.which === 46) {
                var previewImage = self.get('controller.previewImage');
                self.get('controller').send('removeImage', previewImage);
            }
        });
    },

    removeKeyEventHandlers: function () {
        Ember.$(window).unbind("keyup");
    },

    visibleChanged: function () {
        console.log("isVisible changed");
        var visible = this.get('isVisible');
        if (visible) {
            this.setKeyEventHandlers();
        } else {
            this.removeKeyEventHandlers();
        }
    }.observes('isVisible')
});

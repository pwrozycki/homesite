import Ember from 'ember';

export default Ember.View.extend({
    templateName: 'views/image-preview',

    setKeyEventHandlers: function () {
        var self = this;
        Ember.$(window).keyup(function (event) {
            // left arrow
            if (event.which === 37) {
                self.sendAction('prevImage');
            // right arrow
            } else if (event.which === 39) {
                self.sendAction('nextImage');
            // up arrow or escape key
            } else if (event.which === 38 || event.which === 27) {
                self.sendAction('exitPreview');
            }
        });
    },

    removeKeyEventHandlers: function () {
        Ember.$(window).unbind("keyup");
    },

    visibleChanged: function() {
        console.log("isVisible changed");
        var visible = this.get('isVisible');
        if (visible) {
            this.setKeyEventHandlers();
        } else {
            this.removeKeyEventHandlers();
        }
    }.observes('isVisible')
});

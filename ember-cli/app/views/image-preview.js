import Ember from 'ember';

const SWIPE_MOVE_THRESHOLD = 50;
const SWIPE_ANGLE_THRESHOLD = 10;

export default Ember.View.extend({
    templateName: 'views/image-preview',
    mouseDownCoords: null,

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
                self.get('controller').send('removeFile', previewImage);
            }
        });
    }.on('didInsertElement'),

    mouseDown: function (event) {
        event.preventDefault();
        this.set('mouseDownCoords', [event.clientX, event.clientY]);
    },

    mouseUp: function (event) {
        console.log('mouseUp');
        var mouseDownCoords = this.get('mouseDownCoords');

        if (!Ember.isEmpty(mouseDownCoords)) {
            var xDelta = event.clientX - mouseDownCoords[0];
            var xDeltaAbs = Math.abs(xDelta);
            var yDelta = event.clientY - mouseDownCoords[1];
            var yDeltaAbs = Math.abs(yDelta);

            if ((xDeltaAbs > SWIPE_MOVE_THRESHOLD || yDeltaAbs > SWIPE_MOVE_THRESHOLD)) {
                // horizontal movement -> switch to either previous or next image
                if (xDeltaAbs != 0 && yDeltaAbs / xDeltaAbs < Math.tan(Math.PI * SWIPE_ANGLE_THRESHOLD / 180)) {
                    if (xDelta > 0) {
                        this.get('controller').send('nextImage');
                    } else {
                        this.get('controller').send('prevImage');
                    }
                }

                // vertical movement -> when up, leave preview
                if (xDeltaAbs == 0 || yDeltaAbs / xDeltaAbs > Math.tan(Math.PI * (90 - SWIPE_ANGLE_THRESHOLD) / 180)) {
                    if (yDelta < 0) {
                        this.get('controller').send('exitPreview', this.get('controller.model'));
                    }
                }
            }

            this.set('mouseDownCoords', null);
        }
    },

    removeKeyEventHandlers: function () {
        Ember.$(window).unbind("keyup");
    }.on('willDestroyElement')
});

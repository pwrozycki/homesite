import Ember from 'ember';

const SWIPE_MOVE_THRESHOLD = 50;
const SWIPE_ANGLE_THRESHOLD = 10;

export default Ember.View.extend({
    templateName: 'views/image-preview',
    touchStartCoords: null,

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

    touchStart: function (event) {
        var touchEvent = event.originalEvent.touches[0];
        //event.preventDefault();
        this.set('touchStartCoords', [touchEvent.clientX, touchEvent.clientY]);
    },

    touchEnd: function (event) {
        var touchStartCoords = this.get('touchStartCoords');
        var touchEvent = event.originalEvent.changedTouches[0];

        if (!Ember.isEmpty(touchStartCoords)) {
            var xDelta = touchEvent.clientX - touchStartCoords[0];
            var xDeltaAbs = Math.abs(xDelta);
            var yDelta = touchEvent.clientY - touchStartCoords[1];
            var yDeltaAbs = Math.abs(yDelta);

            if ((xDeltaAbs > SWIPE_MOVE_THRESHOLD || yDeltaAbs > SWIPE_MOVE_THRESHOLD)) {
                // horizontal movement -> switch to either previous or next image
                if (xDeltaAbs !== 0 && yDeltaAbs / xDeltaAbs < Math.tan(Math.PI * SWIPE_ANGLE_THRESHOLD / 180)) {
                    if (xDelta > 0) {
                        this.get('controller').send('prevImage');
                    } else {
                        this.get('controller').send('nextImage');
                    }
                }

                // vertical movement -> when up, leave preview
                if (xDeltaAbs === 0 || yDeltaAbs / xDeltaAbs > Math.tan(Math.PI * (90 - SWIPE_ANGLE_THRESHOLD) / 180)) {
                    if (yDelta < 0) {
                        this.get('controller').send('exitPreview', this.get('controller.model'));
                    }
                }
            }

            this.set('touchStartCoords', null);
        }
    },

    removeKeyEventHandlers: function () {
        Ember.$(window).unbind("keyup");
    }.on('willDestroyElement')
});

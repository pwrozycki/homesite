import Ember from 'ember';

export default Ember.Component.extend({
    setKeyEventHandlers: function () {
        var self = this;
        $(window).keyup(function (event) {
            // left arrow
            if (event.which == 37) {
                self.sendAction('leftPressed');
            // right arrow
            } else if (event.which == 39) {
                self.sendAction('rightPressed');
            // up arrow or escape key
            } else if (event.which == 38 || event.which == 27) {
                self.sendAction('upPressed');
            }
        });
    },

    removeKeyEventHandlers: function () {
        $(window).unbind("keyup");
    },

    visibleChanged: function() {
        var visible = this.get('isVisible');
        if (visible) {
            this.setKeyEventHandlers();
        } else {
            this.removeKeyEventHandlers();
        }
    }.observes('isVisible'),

    actions: {
        up: function () {
            this.sendAction('upPressed');
        },
        left: function () {
            this.sendAction('leftPressed');
        },
        right: function () {
            this.sendAction('rightPressed');
        },
        remove: function(image) {
            this.sendAction('removePressed', image);
        },
        undo: function(image) {
            this.sendAction('undoPressed', image);
        },
        rotate: function(image) {
            this.sendAction('rotatePressed', image);
        }
    }
});
